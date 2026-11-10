"""Голосовая версия Ники: тот же агент (agent.py), вокруг него — Pipecat.

Цепочка: браузер (микрофон) → Deepgram (речь → текст) → Ника → Cartesia (текст → речь) → браузер (динамик).
Pipecat отвечает только за «уши и рот»: звук, определение конца фразы, перебивания.
Мозг — наш agent.answer(): тот же промпт, инструменты, кэш и логи, что и в текстовой версии.

Запуск:  .venv-voice/bin/python voice.py   → открыть http://localhost:7860 и нажать Connect.
"""

import asyncio
import json
import os
import re
import time
import uuid
from datetime import datetime, timezone

import anthropic
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    Frame,
    LLMContextFrame,
    MetricsFrame,
    TTSSpeakFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.metrics.metrics import TTFBMetricsData
from pipecat.observers.base_observer import BaseObserver, FramePushed
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.transcriptions.language import Language
from pipecat.transports.base_transport import TransportParams

import agent  # наша Ника из текстовой версии

VOICE_ID = "25b7aaa6-1670-42dc-b791-419322400803"  # Cartesia, «Daria — Decisive Dispatcher», русский женский голос

# Голосовые правила (коротко, без списков и ссылок, цифры словами) — дописываем в конец промпта Ники.
# Промпт при этом не меняется от звонка к звонку, поэтому кэш работает так же, как в тексте.
agent.SYSTEM_PROMPT += (agent.ROOT / "prompt_voice.md").read_text(encoding="utf-8")

# Модель для голоса: Opus 5.5, effort medium. Выбор и цифры — ../voice_model_choice.md (09–10.11):
#   eval (22 вопроса × 3, без A1/A2): Sonnet low 86%, Sonnet medium 91%, Opus low 89%, Opus medium 97%;
#   контрольный мини-eval H1–H4: 3/12, 3/12, 11/12, 11/12; запись и заявки (группа C): Opus low 9/12, Opus medium 12/12;
#   пауза без поиска (среднее, Ника + TTS): Sonnet ~1,7–1,8 с, Opus low ~1,9 с, Opus medium ~2,1 с
#   (живые звонки medium — 2,2 с); с поиском Opus low и medium одинаково ~5,1 с; effort на скорость почти не влияет.
# Sonnet быстрее на 0,3–1,7 с, но путает язык и давит на клиента — для поддержки это хуже лишней секунды.
agent.MODEL = "claude-opus-5-5"
agent.EFFORT = "medium"

# Заполнитель: когда Ника вызывает инструмент (поиск в базе, слоты демо, заявка), после него
# будет ещё один вызов модели, то есть +1,5–2 с тишины. В этот момент она коротко говорит, что проверяет.
# Первая версия включала заполнитель по таймеру (1,5 с) и звучала почти на каждой реплике,
# даже на «до свидания»: «у кого вы всё время уточняете?». Поэтому сигнал — сам вызов инструмента.
FILLERS = ["Секунду, проверяю.", "Сейчас посмотрю.", "Так, смотрю."]  # по кругу, чтобы не повторяться

_run_tool = agent.run_tool
on_tool_start = None  # сюда NikaBrain кладёт свой сигнал на время ответа


def run_tool_with_signal(name: str, args: dict):
    """Тот же инструмент Ники, только перед запуском подаёт сигнал «нужен заполнитель»."""
    if on_tool_start:
        on_tool_start()
    return _run_tool(name, args)


agent.run_tool = run_tool_with_signal  # agent.py вызывает инструменты через это имя


def to_speech(text: str) -> str:
    """Убирает то, что нельзя произносить вслух: ссылки и разметку Markdown."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # [текст](ссылка) → текст
    text = re.sub(r"https?://\S+", "", text)  # голые ссылки
    text = re.sub(r"(Подробнее|More details|Details)\s*:\s*", "", text)  # «Подробнее:» без ссылки
    text = re.sub(r"(^|\n)\s*[-•]\s+", r"\1", text)  # дефисы в начале пунктов списка
    text = re.sub(r"[*_#`>]", "", text)  # звёздочки, решётки и т.п.
    return re.sub(r"\s+", " ", text).strip()


class LatencyMeter(BaseObserver):
    """Замер задержки по этапам: смотрит на все кадры конвейера и на каждый ответ пишет одну строку в лог.

    stt_s   — Deepgram: от конца речи до готового текста (его собственная метрика TTFB);
    nika_s  — Ника: от фразы до готового ответа (все вызовы модели и инструменты);
    tts_s   — Cartesia: от текста до первого звука (TTFB);
    first_sound_s — человек замолчал → прозвучал первый звук (заполнитель или ответ);
    answer_s      — человек замолчал → начался сам ответ.
    """

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.turn = None  # данные текущего хода

    def answer_ready(self, nika_s: float, steps: int, filler: bool, text: str):
        """NikaBrain сообщает: ответ готов и отправлен на озвучку."""
        if self.turn is not None:
            self.turn.update(nika_s=round(nika_s, 2), steps=steps, filler=filler, text=text[:80],
                             answer_pushed=time.monotonic())

    async def on_push_frame(self, data: FramePushed):
        if not data.first_push:
            return  # каждый кадр учитываем один раз, а не на каждом звене
        frame, now = data.frame, time.monotonic()
        if isinstance(frame, UserStoppedSpeakingFrame):
            self.turn = {"user_stopped": now}
        elif self.turn is None:
            return
        elif isinstance(frame, MetricsFrame):
            for m in frame.data:
                if isinstance(m, TTFBMetricsData) and m.value:
                    if "Deepgram" in m.processor and "stt_s" not in self.turn:
                        self.turn["stt_s"] = round(m.value, 2)
                    if "Cartesia" in m.processor and "answer_pushed" in self.turn and "tts_s" not in self.turn:
                        self.turn["tts_s"] = round(m.value, 2)
        elif isinstance(frame, BotStartedSpeakingFrame):
            t = self.turn
            t.setdefault("first_sound_s", round(now - t["user_stopped"], 2))
            if "answer_pushed" in t:
                t["answer_s"] = round(now - t["user_stopped"], 2)
                record = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "model": agent.MODEL,
                          "effort": agent.EFFORT,
                          **{k: v for k, v in t.items() if k not in ("user_stopped", "answer_pushed")}}
                with self.path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                logger.info(f"Замер: {record}")
                self.turn = None


class NikaBrain(FrameProcessor):
    """Звено конвейера, внутри которого работает Ника.

    Получает от Pipecat готовую фразу человека (когда он договорил),
    отдаёт её agent.answer() и передаёт ответ дальше — на озвучку.
    """

    def __init__(self, meter: LatencyMeter | None = None):
        super().__init__()
        self.meter = meter  # замер задержки по этапам
        self.client = anthropic.Anthropic()
        self.messages = []  # история диалога Ники — та же, что в текстовой версии
        self.log = {"path": agent.LOGS_DIR / f"voice-{datetime.now():%Y-%m-%d}.jsonl",
                    "meta": {"session": uuid.uuid4().hex[:8], "cache": True, "channel": "voice"}}
        self.turn = 0
        # Очередь фраз человека и один «работник», который отвечает на них строго по одной.
        # Зачем: человек может договорить фразу кусками, пока Ника ещё думает над первым куском.
        # Если запустить два ответа одновременно, они перепутают общую историю — и API начнёт отвечать 400.
        self.pending: list[str] = []
        self.user_seen = 0  # сколько реплик человека из контекста Pipecat уже передано Нике
        self.worker: asyncio.Task | None = None

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        # LLMContextFrame = «человек договорил, вот его фраза». Пробные (speculation) — пропускаем.
        if isinstance(frame, LLMContextFrame) and not frame.speculation:
            # Берём фразу, только если в контексте появилась НОВАЯ реплика человека.
            # Иначе (шум, кашель, нераспознанная речь) Pipecat присылает тот же контекст,
            # и Ника второй раз отвечала на уже отвеченный вопрос — так было в тесте 4.
            user_count = sum(1 for m in frame.context.get_messages() if m.get("role") == "user")
            text = self.last_user_text(frame.context) if user_count > self.user_seen else ""
            self.user_seen = max(self.user_seen, user_count)
            if text:
                self.pending.append(text)
                if self.worker is None or self.worker.done():
                    # Отдельная задача: перебивание (человек заговорил) не обрывает её на середине.
                    self.worker = self.create_task(self.work())
            return  # дальше по конвейеру этот кадр не нужен

        await self.push_frame(frame, direction)  # всё остальное (звук, служебные сигналы) — пропускаем дальше

    @staticmethod
    def last_user_text(context: LLMContext) -> str:
        for m in reversed(context.get_messages()):
            if m.get("role") == "user":
                content = m.get("content")
                if isinstance(content, str):
                    return content.strip()
                return " ".join(p.get("text", "") for p in content if isinstance(p, dict)).strip()
        return ""

    async def work(self):
        while self.pending:
            # Всё, что человек успел сказать, — одним сообщением: «Сколько стоит» + «минута на платформе».
            text = " ".join(self.pending)
            self.pending.clear()
            self.turn += 1
            self.log["meta"]["turn"] = self.turn
            self.messages.append({"role": "user", "content": text})
            logger.info(f"Человек: {text}")
            started, steps, filler_used = time.monotonic(), 0, False
            try:
                # agent.answer — обычная (не async) функция: запускаем её в отдельном потоке,
                # чтобы звук и Pipecat не «замирали», пока Ника думает.
                # Сигнал из потока Ники в Pipecat: «пошла в инструмент». Один раз за ответ.
                global on_tool_start
                loop = asyncio.get_running_loop()
                tool_started = asyncio.Event()
                on_tool_start = lambda: loop.call_soon_threadsafe(tool_started.set)

                thinking = asyncio.ensure_future(
                    asyncio.to_thread(agent.answer, self.client, self.messages, True, self.log))
                signal = asyncio.ensure_future(tool_started.wait())
                # Ждём, что наступит раньше: готовый ответ или вызов инструмента.
                await asyncio.wait({thinking, signal}, return_when=asyncio.FIRST_COMPLETED)
                if signal.done() and not thinking.done() and not self.pending:
                    filler = FILLERS[self.turn % len(FILLERS)]
                    logger.info(f"Заполнитель: {filler}")
                    await self.push_frame(TTSSpeakFrame(filler))
                    filler_used = True
                signal.cancel()
                reply = await thinking
                answer_text, steps = reply.text, reply.steps
                logger.info(f"Ника ({reply.latency_s:.2f} с, шагов {reply.steps}): {answer_text}")
            except anthropic.APIError as e:
                logger.error(f"Ошибка API: {type(e).__name__}")
                answer_text = "Извините, у меня техническая заминка. Повторите, пожалуйста, вопрос через минуту."
            if self.pending:
                # Пока Ника думала, человек сказал ещё что-то: этот ответ уже устарел.
                # Не озвучиваем его, а сразу отвечаем с учётом новой фразы (следующий круг цикла).
                logger.info("Ответ не озвучен: человек продолжил говорить")
                continue
            if self.meter:
                self.meter.answer_ready(time.monotonic() - started, steps, filler_used, answer_text)
            await self.push_frame(TTSSpeakFrame(to_speech(answer_text)))


async def bot(runner_args: RunnerArguments):
    """Pipecat вызывает эту функцию, когда в браузере нажали Connect."""
    agent.load_env()
    agent.LOGS_DIR.mkdir(exist_ok=True)

    # 1. Транспорт: звук из браузера и обратно (WebRTC на localhost).
    transport = await create_transport(runner_args, {
        "webrtc": lambda: TransportParams(audio_in_enabled=True, audio_out_enabled=True),
    })

    # 2. STT: Deepgram nova-3, русский. Режим multi (все языки сразу) на тесте путал русский
    #    с чешским и греческим («na platformě», «Δικτό»), поэтому язык задан явно.
    stt = DeepgramSTTService(
        api_key=os.environ["DEEPGRAM_API_KEY"],
        settings=DeepgramSTTService.Settings(model="nova-3", language="ru"),
    )

    # 3. TTS: Cartesia, русский голос.
    tts = CartesiaTTSService(
        api_key=os.environ["CARTESIA_API_KEY"],
        settings=CartesiaTTSService.Settings(voice=VOICE_ID, language=Language.RU),
    )

    # 4. Определение конца фразы: Silero VAD слушает тишину, сборщик склеивает распознанный текст в одну фразу.
    context = LLMContext()
    user_aggregator, _ = LLMContextAggregatorPair(
        context,
        # empty_user_turn=None: если человек издал звук, но слов не распознано, Ника не отвечает.
        user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer(), empty_user_turn=None),
    )

    # Замер по этапам → logs/voice-latency.jsonl (одна строка на ответ).
    meter = LatencyMeter(agent.LOGS_DIR / "voice-latency.jsonl")

    # 5. Сам конвейер: порядок звеньев = порядок, в котором идёт звук и текст.
    pipeline = Pipeline([
        transport.input(),   # микрофон
        stt,                 # речь → текст
        user_aggregator,     # ждёт, пока человек договорит
        NikaBrain(meter),    # Ника отвечает
        tts,                 # текст → речь
        transport.output(),  # динамик
    ])

    task = PipelineTask(pipeline, params=PipelineParams(enable_metrics=True), observers=[meter])

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        # Приветствие сразу после подключения, чтобы было понятно, что связь есть.
        await task.queue_frames([TTSSpeakFrame("Здравствуйте! Это Ника, поддержка SpeakNode. Чем могу помочь?")])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        await task.cancel()

    await PipelineRunner(handle_sigint=runner_args.handle_sigint).run(task)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
