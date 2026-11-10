# Nika - SpeakNode support agent: text and voice

> Nika is a support agent for SpeakNode (voice AI platform), built on the raw Anthropic API (Claude Opus 5.5) without frameworks: system prompt, 4 tools, a 15-document knowledge base. Prompt caching makes it 3.44× cheaper per eval run (89% of input tokens read from cache). A 24-case eval with an LLM judge passes 71/72 dialogs, including 15/15 prompt-injection attempts.
>
> The voice version is the same agent inside a Pipecat pipeline: Deepgram (speech to text) → Nika → Cartesia (text to speech). Opus 5.5 medium was chosen for voice after comparing four model/effort settings: 97% on the voice eval, 11/12 on a control mini-eval, ~2.2 s from the end of the caller's phrase to the answer.

## Contents

| Что | Файл |
|---|---|
| **Текстовый агент** | |
| Отчёт по кэшу (стоимость и доля кэша до / после) | [cache_report.md](cache_report.md) |
| Отчёт по тестам (24 кейса, 5 prompt injection) | [test_report.md](test_report.md) |
| Тест-кейсы с критериями | [eval_cases.md](eval_cases.md) · [tests.json](speaknode-agent/tests.json) |
| Агент: цикл, кэш, логи | [agent.py](speaknode-agent/agent.py) |
| Инструменты: поиск по базе, демо, заявка, оператор | [tools.py](speaknode-agent/tools.py) |
| Системный промпт | [prompt.md](speaknode-agent/prompt.md) (рус. версия - [prompt_ru.md](speaknode-agent/prompt_ru.md)) |
| База знаний, 15 документов | [kb/](speaknode-agent/kb/) |
| Прогонщик eval и судья | [run_eval.py](speaknode-agent/run_eval.py) |
| **Голосовая версия** | |
| Выбор модели и замер задержки по этапам | [voice_model_choice.md](voice_model_choice.md) |
| Голосовая Ника: Pipecat, заполнитель, очередь фраз, замер задержки | [voice.py](speaknode-agent/voice.py) |
| Голосовые правила промпта | [prompt_voice.md](speaknode-agent/prompt_voice.md) |
| Контрольный мини-eval H1–H4 | [tests_holdout.json](speaknode-agent/tests_holdout.json) |
| **Данные** | |
| Сырые результаты прогонов | [eval_results/](speaknode-agent/eval_results/) · логи вызовов [logs/](speaknode-agent/logs/) |

## How to run

Текстовый агент:

```bash
cd speaknode-agent
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
echo 'ANTHROPIC_API_KEY=...' > .env      # свой ключ
.venv/bin/python agent.py                 # чат с Никой, /exit - выход
.venv/bin/python run_eval.py --runs 1     # eval: 24 кейса
```

Голосовая версия (нужны ещё ключи Deepgram и Cartesia в том же `.env`):

```bash
cd speaknode-agent
python3 -m venv .venv-voice && .venv-voice/bin/pip install -r requirements-voice.txt
echo 'DEEPGRAM_API_KEY=...' >> .env
echo 'CARTESIA_API_KEY=...' >> .env
.venv-voice/bin/python voice.py           # открыть http://localhost:7860 и нажать Connect
```
