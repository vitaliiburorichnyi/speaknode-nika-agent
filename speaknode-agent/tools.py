"""Инструменты агента: описания для модели (JSON Schema) и код, который их выполняет."""

import html
import json
import math
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import snowballstemmer

ROOT = Path(__file__).parent
KB_DIR = ROOT / "kb"
TICKETS_FILE = ROOT / "tickets.jsonl"
DEMO_FILE = ROOT / "demo_bookings.jsonl"
HANDOFFS_FILE = ROOT / "handoffs.jsonl"
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")

# Описания инструментов. Порядок фиксированный: от него зависит кэш.
TOOLS = [
    {
        "name": "search_kb",
        "description": (
            "Searches the SpeakNode knowledge base (website and docs, in English). "
            "It covers two different products, do not mix them up: Managed service (the SpeakNode team builds "
            "and runs the agent, flat monthly fee) and Platform (the client builds agents, pays per voice minute). "
            "Call it before any answer about SpeakNode facts: prices, features, integrations, phone numbers, data. "
            "This is keyword search, not semantic: write the query in English even if the person writes in another "
            "language, and add synonyms. If the results do not answer the question, search again with other words. "
            "Returns up to 5 sections, each in a <document> tag with file, title and source link. "
            "If there is still no answer after the second search, say you do not know and offer a ticket."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Query in English: 3-10 keywords including synonyms. "
                        "Use the words a page would use, not only product names. "
                        "Example for 'how much is a minute?': 'cost per voice minute price free minutes'."
                    ),
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "create_ticket",
        "description": (
            "Creates a request for the SpeakNode team, who reply later by email: a demo when no book_demo slot fits, "
            "an exact quote, a question the knowledge base cannot answer, a complaint. "
            "Call it only after the person has given name and email and agreed to the request."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Person's name."},
                "email": {"type": "string", "description": "Person's email, exactly as they wrote it."},
                "topic": {
                    "type": "string",
                    "enum": ["demo", "pricing", "question", "complaint"],
                    "description": "Request topic.",
                },
                "summary": {
                    "type": "string",
                    "description": "1-3 sentences for the team: the person's business, their task, what they want.",
                },
            },
            "required": ["name", "email", "topic", "summary"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "book_demo",
        "description": (
            "Books a 30-minute online SpeakNode demo. Two steps. "
            "Step 1: call with slot = null to get free slots (UTC) and offer the person 2-3 of them. "
            "Step 2: call with a slot only after the person has picked a time and confirmed name and email. "
            "Calling again with the same email and slot does not create a second booking."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": ["string", "null"], "description": "Person's name. null in step 1."},
                "email": {"type": ["string", "null"], "description": "Person's email. null in step 1."},
                "slot": {
                    "type": ["string", "null"],
                    "description": "Slot exactly as in the free list, e.g. '2026-11-03 10:00 UTC'. "
                                   "null to get the free slots.",
                },
            },
            "required": ["name", "email", "slot"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "handoff_to_human",
        "description": (
            "Hands the conversation to a live SpeakNode operator right now. Unlike create_ticket, the person "
            "does not wait for an email. Call it when: the person asks for an operator or a human; the person is "
            "frustrated and your answers do not help; the topic is refunds, contracts or legal; you failed to "
            "answer twice. Search ordinary questions with search_kb first. "
            "Tell the person about the transfer only after you see the result: operators may be offline."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "enum": ["user_request", "frustrated", "sensitive", "agent_stuck"],
                    "description": "Why: the person asked, the person is frustrated, sensitive topic, you are stuck.",
                },
                "summary": {
                    "type": "string",
                    "description": "1-3 sentences for the operator: who the person is, what they want, what you "
                                   "already answered. So the person does not have to repeat everything.",
                },
            },
            "required": ["reason", "summary"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


# ---------- search_kb: простой BM25 по разделам ----------

# Служебные слова встречаются везде и ничего не говорят о теме, поэтому в поиске их не учитываем.
# Список — стандартный английский от Snowball (snowballstem.org/algorithms/english/stop.txt), 174 слова.
# В файле слово стоит в начале строки, после «|» идёт комментарий. isn't режем как текст: isn + t.
STOP_WORDS = {w for line in (ROOT / "stopwords_en.txt").read_text(encoding="utf-8").splitlines()
              for w in re.findall(r"[a-z]+", line.split("|")[0])}

# Стандартный стеммер Snowball (Porter2): price / prices / priced / pricing -> price.
STEMMER = snowballstemmer.stemmer("english")


def _tokens(text: str) -> list[str]:
    words = re.findall(r"[a-zа-яё0-9]+", text.lower())
    # Русские слова (агент говорит и по-русски) режем по-старому: первые 5 букв.
    return [STEMMER.stemWord(w) if w.isascii() else w[:5] for w in words if len(w) > 1 and w not in STOP_WORDS]


SOURCE_RE = re.compile(r"<!-- source: (\S+) -->\n?")


def _load_chunks() -> list[dict]:
    # Кусок = раздел под заголовком ## (load_kb ставит пустую строку только перед заголовком).
    chunks = []
    for path in sorted(KB_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip()
        source = ""
        for part in text.split("\n\n"):
            # Метка источника стоит перед текстом страницы и действует до следующей метки.
            m = SOURCE_RE.search(part)
            if m:
                source = m.group(1)
                part = SOURCE_RE.sub("", part)
            part = part.strip()
            if not part or part.startswith("# "):
                continue
            for piece in _split_faq(part):
                # Название документа добавляем к словам куска: «Managed pricing» находится
                # по слову pricing, даже если в самом разделе его нет (Contextual Retrieval, 5.3).
                chunks.append({"doc": path.name, "title": title, "source": source,
                               "text": piece, "tokens": _tokens(title + " " + piece)})
    return chunks


def _split_faq(part: str) -> list[str]:
    # Раздел «Частые вопросы» — это 10-15 вопросов в одном куске: нужный ответ тонет в длинном тексте,
    # и поиск его не находит. Такой раздел режем на куски «вопрос + ответ», к каждому — заголовок раздела.
    lines = part.splitlines()
    starts = [i for i, line in enumerate(lines) if line.rstrip().endswith("?")]
    if len(starts) < 3:
        return [part]
    head = "\n".join(lines[:starts[0]])
    bounds = starts + [len(lines)]
    return [(head + "\n" + "\n".join(lines[a:b])).strip() for a, b in zip(bounds, bounds[1:])]


CHUNKS = _load_chunks()


def search_kb(query: str, k: int = 5) -> str:
    q = set(_tokens(query))
    if not q:
        raise ValueError("Empty query. Pass 3-10 English keywords.")
    n = len(CHUNKS)
    avg_len = sum(len(c["tokens"]) for c in CHUNKS) / n
    scored = []
    for c in CHUNKS:
        score = 0.0
        for term in q:
            tf = c["tokens"].count(term)
            if not tf:
                continue
            df = sum(1 for x in CHUNKS if term in x["tokens"])
            idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
            score += idf * tf * 2.2 / (tf + 1.2 * (0.25 + 0.75 * len(c["tokens"]) / avg_len))
        if score > 0:
            scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        return "Nothing found. The knowledge base has no answer to this query."
    # Каждый раздел в теге <document>: промпт говорит, что текст внутри — данные, а не инструкции.
    # source — ссылка, чтобы агент мог сказать клиенту, где прочитать подробнее.
    # html.escape: кавычки и <, > в тексте базы не смогут «закрыть» тег раньше времени.
    return "\n\n".join(f'<document file="{c["doc"]}" title="{html.escape(c["title"])}" '
                       f'source="{html.escape(c["source"])}">\n{html.escape(c["text"], quote=False)}\n</document>'
                       for _, c in scored[:k])


# ---------- create_ticket ----------

def create_ticket(name: str, email: str, topic: str, summary: str) -> str:
    if not EMAIL_RE.fullmatch(email):
        raise ValueError("The email looks invalid. Ask the person to check it.")
    # Идемпотентность: та же заявка второй раз (повторный вызов модели) — возвращаем первую.
    if TICKETS_FILE.exists():
        for line in TICKETS_FILE.read_text(encoding="utf-8").splitlines():
            old = json.loads(line) if line else {}
            if (old.get("email", "").lower(), old.get("topic"), old.get("summary")) == (email.lower(), topic, summary):
                return f"Request {old['id']} already exists. The team will reply to {email}."
    ticket = {
        "id": "T-" + uuid.uuid4().hex[:6].upper(),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "name": name, "email": email, "topic": topic, "summary": summary,
    }
    with TICKETS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ticket, ensure_ascii=False) + "\n")
    return f"Request {ticket['id']} created. The team will reply to {email}."


# ---------- book_demo ----------

def _demo_slots() -> list[str]:
    # Ненастоящий календарь: ближайшие 3 рабочих дня, 10:00 и 15:00 UTC.
    day = datetime.now(timezone.utc).date()
    slots = []
    while len(slots) < 6:
        day += timedelta(days=1)
        if day.weekday() < 5:  # 0-4 = понедельник-пятница
            slots += [f"{day} 10:00 UTC", f"{day} 15:00 UTC"]
    return slots


def _bookings() -> list[dict]:
    if not DEMO_FILE.exists():
        return []
    return [json.loads(line) for line in DEMO_FILE.read_text(encoding="utf-8").splitlines() if line]


def book_demo(name: str | None, email: str | None, slot: str | None) -> str:
    bookings = _bookings()
    taken = {b["slot"] for b in bookings}
    free = [s for s in _demo_slots() if s not in taken]
    if slot is None:
        return "Free demo slots: " + ", ".join(free)
    if not name or not email:
        raise ValueError("Name and email are required to book. Ask the person for them.")
    if not EMAIL_RE.fullmatch(email):
        raise ValueError("The email looks invalid. Ask the person to check it.")
    # Идемпотентность: тот же человек и то же время — возвращаем старую запись, не создаём дубль.
    # Смотрим только будущие записи: после прошедшего демо человек может записаться снова.
    upcoming = set(_demo_slots())
    for b in bookings:
        if b["email"].lower() == email.lower() and b["slot"] in upcoming:
            if b["slot"] == slot:
                return "This demo is already booked for this email and slot. Not booking again."
            # Без чужих данных: по чужому email нельзя узнать, есть ли у человека демо и на какое время.
            raise ValueError("Could not book this slot for this email. "
                             "To change an existing booking or if this repeats, offer the person a ticket.")
    if slot not in free:
        raise ValueError(f"This slot is not available. Free: {', '.join(free)}.")
    booking = {
        "id": "D-" + uuid.uuid4().hex[:6].upper(),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "name": name, "email": email, "slot": slot,
    }
    with DEMO_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(booking, ensure_ascii=False) + "\n")
    return f"Demo {booking['id']} booked for {slot}. The invite will be sent to {email}."


# ---------- handoff_to_human ----------

def _operators_online(now: datetime) -> bool:
    # Ненастоящий график операторов: будни, 08:00-18:00 UTC.
    return now.weekday() < 5 and 8 <= now.hour < 18


def handoff_to_human(reason: str, summary: str) -> str:
    if not summary.strip():
        raise ValueError("Empty summary. Write 1-3 sentences for the operator about the person and their question.")
    now = datetime.now(timezone.utc)
    if not _operators_online(now):
        # Не ошибка, а обычная ситуация: операторов нет — предлагаем заявку.
        return ("No operators right now: they work Monday-Friday 08:00-18:00 UTC. "
                "Apologise and offer a ticket, the team will reply by email.")
    handoff = {
        "id": "H-" + uuid.uuid4().hex[:6].upper(),
        "created_at": now.isoformat(timespec="seconds"),
        "reason": reason, "summary": summary,
    }
    with HANDOFFS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(handoff, ensure_ascii=False) + "\n")
    # В голосовой версии здесь был бы перевод звонка на номер оператора.
    return (f"Handed off to an operator ({handoff['id']}), wait time about 2 minutes. "
            "Tell the person an operator is joining and do not answer on substance any more.")


HANDLERS = {"search_kb": search_kb, "create_ticket": create_ticket, "book_demo": book_demo,
            "handoff_to_human": handoff_to_human}


def run_tool(name: str, args: dict) -> tuple[str, bool]:
    """Выполняет инструмент. Возвращает (текст результата, is_error)."""
    handler = HANDLERS.get(name)
    if handler is None:
        return f"Unknown tool '{name}'. Available: {', '.join(HANDLERS)}.", True
    try:
        return handler(**args), False
    except ValueError as e:
        # Ошибка понятным текстом, чтобы модель могла исправиться.
        return f"Error: {e}", True
    except Exception as e:
        # Любая другая ошибка — сбой в нашем коде, а не ошибка модели. Агент не падает, модель предлагает заявку.
        return (f"Internal error in the tool ({type(e).__name__}). Do not retry; "
                "apologise and offer the person a ticket."), True
