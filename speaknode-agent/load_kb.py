"""Загрузчик базы знаний: скачивает страницы speaknode.com и docs.speaknode.com
и собирает из них 15 документов по темам в папку kb/.

Запуск: .venv/bin/python load_kb.py
"""

import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

KB_DIR = Path(__file__).parent / "kb"
SITE = "https://www.speaknode.com"
DOCS = "https://docs.speaknode.com/en"

# Тема -> список источников. Источник: URL или (URL, текст начала куска, текст конца куска),
# если с длинной страницы нужен только один раздел.
TOPICS = {
    "01_what_is_speaknode": [(f"{SITE}/", None, "The cost of a ringing phone"),
                             (f"{SITE}/", "Common questions", "Is SpeakNode HIPAA"), f"{DOCS}/features"],
    "02_managed_service": [(f"{SITE}/", "Done for you", "ROI calculator")],
    "03_managed_pricing": [(f"{SITE}/", "Pricing", "Common questions")],
    "04_platform_pricing_billing": [f"{DOCS}/features/billing", f"{DOCS}/guide/billing"],
    "05_industries_and_demos": [f"{SITE}/solutions/ai-medical-receptionist",
                                f"{SITE}/solutions/ai-lead-qualification", f"{SITE}/demos"],
    "06_vs_alternatives": [f"{SITE}/compare/vapi-alternatives"],
    "07_data_security": [(f"{SITE}/", "Is SpeakNode HIPAA", None),
                         (f"{SITE}/solutions/ai-medical-receptionist", "Compliance and data handling", "One flat fee"),
                         f"{DOCS}/lifecycle-support"],
    "08_first_agent": [f"{DOCS}/features/agents", f"{DOCS}/guide/agents", f"{DOCS}/guide/variables"],
    "09_voice_languages_models": [f"{DOCS}/features/voice"],
    "10_prompts_testing": [f"{DOCS}/guide/prompting", f"{DOCS}/guide/testing",
                           f"{DOCS}/guide/best-practices"],
    "11_phone_numbers_sip": [f"{DOCS}/features/telephony", f"{DOCS}/guide/phone-numbers",
                             f"{DOCS}/guide/custom-sip"],
    "12_outbound_campaigns": [f"{DOCS}/features/campaigns", f"{DOCS}/guide/campaigns"],
    "13_integrations_tools": [f"{DOCS}/features/tools", f"{DOCS}/guide/tools", f"{DOCS}/guide/system-tools",
                              f"{DOCS}/guide/webhooks", f"{DOCS}/guide/mcp"],
    "14_website_widget": [f"{DOCS}/features/widget", f"{DOCS}/guide/widget"],
    "15_conversations_analytics_teams": [f"{DOCS}/features/analytics", f"{DOCS}/guide/conversations",
                                         f"{DOCS}/guide/call-analytics", f"{DOCS}/features/teams",
                                         f"{DOCS}/guide/spaces"],
}


class MainText(HTMLParser):
    """Берёт текст только из <main> или <article>: без меню, подвала и скриптов."""
    SKIP = {"script", "style", "nav", "svg"}  # <button> не пропускаем: в нём вопросы FAQ
    BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "tr", "pre", "summary", "div", "br"}

    def __init__(self):
        super().__init__()
        self.depth, self.parts = 0, []
        self.skipping = []  # стек открытых тегов, внутри которых текст не берём

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class") or ""
        # Карточки «предыдущая / следующая страница» в документации: ссылки с рамкой.
        # Без этого в документ про оплату попадали заголовки чужих тем.
        is_card = tag == "a" and "border" in cls
        if tag in ("main", "article"):
            self.depth += 1
        elif tag in self.SKIP or is_card:
            self.skipping.append(tag)
        if self.depth and tag in ("h1", "h2", "h3"):
            self.parts.append("\n\n## ")  # пустая строка только перед заголовком: кусок = раздел
        elif self.depth and tag in self.BLOCK:
            self.parts.append("\n")
        elif self.depth and tag in ("td", "th"):
            self.parts.append(" | ")  # иначе ячейки таблицы склеиваются: "UploadAudio goes..."

    def handle_endtag(self, tag):
        if tag in ("main", "article"):
            self.depth -= 1
        elif self.skipping and tag == self.skipping[-1]:
            self.skipping.pop()

    def handle_data(self, data):
        if self.depth and not self.skipping:
            self.parts.append(data)


_cache: dict[str, str] = {}


def page_text(url: str) -> str:
    if url not in _cache:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (kb-loader)"})
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
        parser = MainText()
        parser.feed(html)
        text = "".join(parser.parts)
        text = re.sub(r"[ \t\xa0]+", " ", text)
        # Внутри раздела строки идут подряд, а пустая строка остаётся только перед "## ".
        # Иначе разбивка на абзацы случайная: заголовок отрывается от своего текста.
        text = re.sub(r"\s*\n\s*", "\n", text).replace("\n## ", "\n\n## ")
        text = re.sub(r"\n\n##[ \t]*(?=\n|$)", "", text)  # пустые заголовки (иконки)
        # Заголовок, сразу за которым идёт подзаголовок, приклеиваем к нему: иначе он один в куске.
        _cache[url] = re.sub(r"(\n\n## [^\n]*)\n\n(?=## )", r"\1\n", text).strip()
    return _cache[url]


def cut(text: str, start: str | None, end: str | None) -> str:
    """Вырезает кусок страницы между двумя заголовками (без учёта регистра)."""
    a = 0
    if start:
        m = re.search(re.escape(start), text, re.IGNORECASE)
        if not m:
            raise ValueError(f"Не нашёл начало раздела: {start!r}")
        a = m.start()
    b = len(text)
    if end:
        m = re.compile(re.escape(end), re.IGNORECASE).search(text, a + 1)
        if not m:
            raise ValueError(f"Не нашёл конец раздела: {end!r}")
        b = m.start()
    # Если конец раздела — заголовок, перед ним остаётся "##" от этого заголовка: убираем.
    return text[a:b].strip().removesuffix("##").strip()


def main():
    # Сначала собираем все документы в памяти. Если хоть одна страница не скачалась
    # или раздел не нашёлся, скрипт падает здесь, а старая база остаётся целой.
    docs = {}
    for name, sources in TOPICS.items():
        pieces = []
        for src in sources:
            url, start, end = src if isinstance(src, tuple) else (src, None, None)
            pieces.append(f"<!-- source: {url} -->\n{cut(page_text(url), start, end)}")
        docs[name] = f"# {name[3:].replace('_', ' ').capitalize()}\n\n" + "\n\n".join(pieces) + "\n"

    KB_DIR.mkdir(exist_ok=True)
    for old in KB_DIR.glob("*.md"):
        old.unlink()  # только теперь удаляем старое: база всегда собирается с нуля
    for name, doc in docs.items():
        (KB_DIR / f"{name}.md").write_text(doc, encoding="utf-8")
        print(f"{name}.md  {len(doc.split()):>6} words  from {len(TOPICS[name])} source(s)")


if __name__ == "__main__":
    main()
