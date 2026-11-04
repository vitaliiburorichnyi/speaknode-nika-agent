# Nika — SpeakNode text support agent

> Nika is a text support agent for SpeakNode (voice AI platform), built on the raw Anthropic API (Claude Opus 5.5) without frameworks: system prompt, 4 tools, a 15-document knowledge base. Prompt caching makes it 3.44× cheaper per eval run (89% of input tokens read from cache). A 24-case eval with an LLM judge passes 71/72 dialogs, including 15/15 prompt-injection attempts.

## Contents

| Что | Файл |
|---|---|
| Отчёт по кэшу (стоимость и доля кэша до / после) | [cache_report.md](cache_report.md) |
| Отчёт по тестам (24 кейса, 5 prompt injection) | [test_report.md](test_report.md) |
| Тест-кейсы с критериями | [eval_cases.md](eval_cases.md) · [tests.json](speaknode-agent/tests.json) |
| Агент: цикл, кэш, логи | [agent.py](speaknode-agent/agent.py) |
| Инструменты: поиск по базе, демо, заявка, оператор | [tools.py](speaknode-agent/tools.py) |
| Системный промпт | [prompt.md](speaknode-agent/prompt.md) (рус. версия — [prompt_ru.md](speaknode-agent/prompt_ru.md)) |
| База знаний, 15 документов | [kb/](speaknode-agent/kb/) |
| Прогонщик eval и судья | [run_eval.py](speaknode-agent/run_eval.py) |
| Сырые результаты прогонов | [eval_results/](speaknode-agent/eval_results/) · логи вызовов [logs/](speaknode-agent/logs/) |

## How to run

```bash
cd speaknode-agent
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
echo 'ANTHROPIC_API_KEY=...' > .env      # свой ключ
.venv/bin/python agent.py                 # чат с Никой, /exit — выход
.venv/bin/python run_eval.py --runs 1     # eval: 24 кейса
```
