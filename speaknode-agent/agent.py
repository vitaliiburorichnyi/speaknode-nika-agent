"""Цикл агента поддержки SpeakNode: вопрос → модель → инструменты → ответ. Плюс кэш и логи.

Запуск в терминале (из папки speaknode-agent):
    .venv/bin/python agent.py             — с кэшем
    .venv/bin/python agent.py --no-cache  — без кэша, для сравнения в отчёте
"""

import argparse
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import anthropic

from tools import TOOLS, run_tool

ROOT = Path(__file__).parent
LOGS_DIR = ROOT / "logs"
SYSTEM_PROMPT = (ROOT / "prompt.md").read_text(encoding="utf-8")

MODEL = "claude-opus-5-5"
EFFORT = "medium"  # глубина размышлений модели: low / medium / high
MAX_TOKENS = 16000  # потолок длины одного ответа модели
MAX_STEPS = 8  # защита от зацикливания: не больше 8 вызовов модели на одно сообщение человека
# Цены за 1 млн токенов, $: вход, выход, запись в кэш (1,25 × вход), чтение из кэша.
# Кроме нашей модели — модели, на которые API может переключиться при отказе (fallback).
PRICES = {
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_write": 5.00, "cache_read": 0.20},
    "claude-opus-5": {"input": 5.00, "output": 25.00, "cache_write": 6.25, "cache_read": 0.50},
    "claude-opus-4-8": {"input": 5.00, "output": 25.00, "cache_write": 6.25, "cache_read": 0.50},
}

REFUSAL_REPLY = "Sorry, I can't help with this request. / Извините, с этим запросом я помочь не могу."
EMPTY_REPLY = "Sorry, I couldn't form an answer. Could you rephrase? / Не получилось ответить. Переформулируете?"
TOO_LONG_REPLY = "Sorry, my answer got too long. Could you ask more briefly? / Ответ получился слишком длинным. Спросите короче?"
ERROR_NOTE = "(Technical error: the reply was not delivered to the person.)"  # пометка в истории после сбоя


@dataclass
class Reply:
    """Итог одного сообщения человека: текст ответа и что происходило. Нужен тестам и голосовой версии."""
    text: str
    outcome: str  # answered / refusal / too_long / empty
    steps: int = 0
    tools: list = field(default_factory=list)  # [(имя инструмента, была ли ошибка)]
    cost_usd: float = 0.0
    latency_s: float = 0.0


def load_env() -> None:
    # Читаем .env сами (строки KEY=VALUE), чтобы не ставить ради этого библиотеку. Ключ никуда не печатаем.
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition("=")
        if sep and key.strip() and not key.startswith("#"):
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def call_model(client: anthropic.Anthropic, messages: list, use_cache: bool, last_step: bool):
    system = [{"type": "text", "text": SYSTEM_PROMPT}]
    extra = {}
    if use_cache:
        # Метка кэша на конце промпта: в кэш идут инструменты + промпт, они стоят в запросе первыми.
        system[0]["cache_control"] = {"type": "ephemeral"}
        # Автокэш хвоста: растущая история диалога на следующем шаге тоже читается из кэша.
        extra["cache_control"] = {"type": "ephemeral"}
    if last_step:
        # Последний разрешённый шаг: инструменты запрещены, модель должна ответить текстом.
        extra["tool_choice"] = {"type": "none"}
    return client.beta.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        tools=TOOLS,
        messages=messages,
        output_config={"effort": EFFORT},
        # Если фильтры безопасности модели откажут, API сам повторит запрос на другой модели.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        **extra,
    )


def content_to_keep(content: list) -> list:
    # Если модель отказала и ответ дописала другая модель, блоки до переключения (кроме текста)
    # обратно не отправляем: так требует API. Обычно переключения нет, и возвращается всё.
    last = max((i for i, b in enumerate(content) if b.type == "fallback"), default=-1)
    return [b for i, b in enumerate(content) if i > last or b.type == "text"]


def usage_stats(usage, model: str) -> dict:
    """Токены и цена вызова. При переключении модели usage.iterations содержит каждую попытку отдельно."""
    attempts = usage.iterations or [usage]
    stats = {"input_tokens": 0, "output_tokens": 0, "cache_write_tokens": 0, "cache_read_tokens": 0, "cost_usd": 0.0}
    unknown_price = False
    for a in attempts:
        # Цена по модели, которая реально отвечала: после отказа это может быть не наша модель.
        # Попытка без имени модели: "message" — наша модель, иначе — та, что вернула ответ.
        name = getattr(a, "model", None) or (MODEL if getattr(a, "type", "") == "message" else model)
        unknown_price = unknown_price or name not in PRICES
        price = PRICES.get(name, PRICES[MODEL])
        tokens = {"input_tokens": a.input_tokens, "output_tokens": a.output_tokens,
                  "cache_write_tokens": a.cache_creation_input_tokens or 0,
                  "cache_read_tokens": a.cache_read_input_tokens or 0}
        for k, v in tokens.items():
            stats[k] += v
        stats["cost_usd"] += (tokens["input_tokens"] * price["input"] + tokens["output_tokens"] * price["output"]
                              + tokens["cache_write_tokens"] * price["cache_write"]
                              + tokens["cache_read_tokens"] * price["cache_read"]) / 1_000_000
    stats["cost_usd"] = round(stats["cost_usd"], 6)
    stats["fallback_ran"] = any(getattr(a, "type", "") == "fallback_message" for a in attempts)
    stats["price_unknown"] = unknown_price  # модель не из таблицы PRICES: цена посчитана приблизительно
    return stats


def write_log(log: dict, record: dict) -> None:
    # Одна строка JSON на одно событие: вызов модели, вызов инструмента, ошибка, итог сообщения.
    record = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), **log["meta"], **record}
    with log["path"].open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def finish_turn(messages: list, turn_start: int, reply: Reply, outcome: str, text: str) -> Reply:
    """Завершает сообщение не обычным ответом модели (отказ, обрыв, пусто, сбой) и приводит историю в порядок,
    чтобы следующий запрос был правильным: роли чередуются, у каждого вызова инструмента есть результат."""
    reply.outcome, reply.text = outcome, text
    if len(messages) == turn_start + 1:
        # Ничего не успело произойти: убираем вопрос из истории, следующий пойдёт в чистый контекст.
        del messages[turn_start:]
        return reply
    # Инструменты уже работали (например, создана заявка): историю оставляем, чтобы модель об этом знала.
    last = messages[-1]
    if last["role"] == "user" and isinstance(last["content"], list):
        # Если прервали посреди инструментов, у невыполненных вызовов ставим результат «прервано».
        answered = {r["tool_use_id"] for r in last["content"]}
        for block in messages[-2]["content"]:
            if block.type == "tool_use" and block.id not in answered:
                last["content"].append({"type": "tool_result", "tool_use_id": block.id,
                                        "content": "Interrupted, not executed.", "is_error": True})
    # Ответ, который написала не модель, а код, тоже пишем в историю: модель увидит, что человек его получил.
    messages.append({"role": "assistant", "content": [{"type": "text", "text": text}]})
    return reply


def answer(client: anthropic.Anthropic, messages: list, use_cache: bool, log: dict) -> Reply:
    """Отвечает на последнее сообщение человека в messages. Дописывает в messages весь ход разговора."""
    turn_start = len(messages) - 1  # где в истории лежит сообщение человека
    turn_started = time.monotonic()
    reply = Reply(text="", outcome="answered")
    try:
        for step in range(1, MAX_STEPS + 1):
            reply.steps = step
            started = time.monotonic()
            response = call_model(client, messages, use_cache, last_step=(step == MAX_STEPS))
            stats = usage_stats(response.usage, response.model)
            reply.cost_usd += stats["cost_usd"]
            write_log(log, {
                "event": "model_call", "step": step, "model": response.model, "request_id": response._request_id,
                "latency_s": round(time.monotonic() - started, 2), "stop_reason": response.stop_reason,
                "refusal_category": getattr(response.stop_details, "category", None), **stats,
            })
            text = "".join(b.text for b in response.content if b.type == "text").strip()

            if response.stop_reason == "refusal":
                return finish_turn(messages, turn_start, reply, "refusal", REFUSAL_REPLY)
            if response.stop_reason == "max_tokens":
                # Ответ обрезан на середине: обрывок в историю не кладём (обрезанный вызов инструмента сломает запрос).
                return finish_turn(messages, turn_start, reply, "too_long", TOO_LONG_REPLY)
            if response.stop_reason != "tool_use" and not text:
                # Модель только подумала и ничего не написала.
                return finish_turn(messages, turn_start, reply, "empty", EMPTY_REPLY)

            # Весь ответ модели (текст, размышления, вызовы инструментов) — в историю без изменений.
            messages.append({"role": "assistant", "content": content_to_keep(response.content)})
            if response.stop_reason != "tool_use":
                reply.text = text
                return reply

            # Модель попросила инструменты: выполняем все и возвращаем результаты одним сообщением.
            # Сообщение с результатами кладём в историю сразу и заполняем по ходу: если прервут, сделанное не потеряется.
            results = []
            messages.append({"role": "user", "content": results})
            for block in content_to_keep(response.content):
                if block.type != "tool_use":
                    continue
                started = time.monotonic()
                tool_text, is_error = run_tool(block.name, block.input)
                reply.tools.append((block.name, is_error))
                write_log(log, {"event": "tool_call", "step": step, "tool": block.name, "is_error": is_error,
                                "latency_s": round(time.monotonic() - started, 3),
                                # Запрос поиска пишем в лог: по нему проверяем качество поиска.
                                # Данные других инструментов (имя, email) не пишем: это личные данные.
                                "query": block.input.get("query") if block.name == "search_kb" else None})
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": tool_text,
                                "is_error": is_error})

        # Сюда не попадаем: на последнем шаге инструменты запрещены, и модель отвечает текстом.
        return finish_turn(messages, turn_start, reply, "empty", EMPTY_REPLY)
    except BaseException as e:
        # Любой сбой (API, Ctrl+C, ошибка в коде): записываем в лог, чиним историю и передаём ошибку дальше.
        outcome = "interrupted" if isinstance(e, KeyboardInterrupt) else "error"
        write_log(log, {"event": "error", "step": reply.steps, "error": type(e).__name__,
                        "status": getattr(e, "status_code", None)})
        finish_turn(messages, turn_start, reply, outcome, ERROR_NOTE)
        raise
    finally:
        reply.cost_usd = round(reply.cost_usd, 6)
        reply.latency_s = round(time.monotonic() - turn_started, 2)
        write_log(log, {"event": "turn_done", "steps": reply.steps, "outcome": reply.outcome,
                        "tools": [name for name, _ in reply.tools], "cost_usd": reply.cost_usd,
                        "latency_s": reply.latency_s})


def main() -> None:
    parser = argparse.ArgumentParser(description="Агент поддержки SpeakNode в терминале")
    parser.add_argument("--no-cache", action="store_true", help="выключить кэш (для сравнения в отчёте)")
    args = parser.parse_args()

    load_env()
    client = anthropic.Anthropic()
    LOGS_DIR.mkdir(exist_ok=True)
    log = {"path": LOGS_DIR / f"{datetime.now():%Y-%m-%d}.jsonl",
           "meta": {"session": uuid.uuid4().hex[:8], "cache": not args.no_cache}}
    messages = []

    print("Ника, поддержка SpeakNode. /exit — выход.")
    turn = 0
    while True:
        try:
            text = input("\nВы: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            # Случайный Enter не обрывает разговор: история диалога сохраняется.
            continue
        if text.lower() == "/exit":
            break
        turn += 1
        log["meta"]["turn"] = turn
        messages.append({"role": "user", "content": text})
        try:
            reply = answer(client, messages, use_cache=not args.no_cache, log=log)
        except KeyboardInterrupt:
            break
        except anthropic.AuthenticationError:
            print("\nОшибка: неверный API-ключ. Проверь ANTHROPIC_API_KEY в файле .env.")
            return
        except anthropic.APIError as e:
            # Лимит, нет связи, сервер не ответил и т.п. История уже приведена в порядок — можно спросить снова.
            print(f"\nОшибка API ({type(e).__name__}). Повтори вопрос через минуту.")
            continue
        except Exception as e:
            # Ошибка в нашем коде: разговор не обрываем, история уже приведена в порядок.
            print(f"\nВнутренняя ошибка ({type(e).__name__}). Повтори вопрос.")
            continue
        print(f"\nНика: {reply.text}")


if __name__ == "__main__":
    main()
