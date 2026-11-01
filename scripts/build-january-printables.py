"""Build the January printables (Nov 2026 batch):

  public/downloads/bible-reading-plan-2027.pdf          whole Bible, 365 days
  public/downloads/new-testament-reading-plan-2027.pdf  New Testament, one chapter each weekday
  public/downloads/21-day-prayer-fasting-journal.pdf    21-day prayer & fasting journal
  public/downloads/soap-30-day-plan-january.pdf         30 SOAP passages for January

Readings come from the book/chapter list of the app's bundled KJV
(../Sermon 2.0/.../Resources/Bible/KJV.json), never typed by hand, and the
script stops if the totals are off (1,189 chapters in the Bible, 260 in the NT)
or a passage reference doesn't exist. The whole-Bible plan splits by verse
count, so each day is a similar amount of reading (Psalm 119 gets a day to itself).

Every PDF ends with a QR code + App Store link carrying its own ct tag.

Run:  python3 scripts/build-january-printables.py
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS = ROOT / "public/downloads"
KJV = Path("/Users/arthurs/Claude Code Projects/Sermon 2.0/Sermon 2.0/Resources/Bible/KJV.json")
SITE_URL = "https://sermonkeeper.app"
YEAR = 2027

W, H = 612, 792
LEFT, RIGHT = 54, 558
NAVY = HexColor("#0C2882")
GRAY = HexColor("#6B7280")
RULE = HexColor("#CBD5E1")
TINT = HexColor("#EFF6FF")
INK = HexColor("#1F2937")


def app_url(ct: str) -> str:
    return f"https://apps.apple.com/app/apple-store/id6758739935?pt=128512327&ct={ct}&mt=8"


# ---------- Bible data ----------

ABBR = {
    "Genesis": "Gen", "Exodus": "Exod", "Leviticus": "Lev", "Numbers": "Num", "Deuteronomy": "Deut",
    "Joshua": "Josh", "Judges": "Judg", "Ruth": "Ruth", "1 Samuel": "1 Sam", "2 Samuel": "2 Sam",
    "1 Kings": "1 Kgs", "2 Kings": "2 Kgs", "1 Chronicles": "1 Chr", "2 Chronicles": "2 Chr",
    "Ezra": "Ezra", "Nehemiah": "Neh", "Esther": "Esth", "Job": "Job", "Psalms": "Ps",
    "Proverbs": "Prov", "Ecclesiastes": "Eccl", "Song of Solomon": "Song", "Isaiah": "Isa",
    "Jeremiah": "Jer", "Lamentations": "Lam", "Ezekiel": "Ezek", "Daniel": "Dan", "Hosea": "Hos",
    "Joel": "Joel", "Amos": "Amos", "Obadiah": "Obad", "Jonah": "Jonah", "Micah": "Mic",
    "Nahum": "Nah", "Habakkuk": "Hab", "Zephaniah": "Zeph", "Haggai": "Hag", "Zechariah": "Zech",
    "Malachi": "Mal", "Matthew": "Matt", "Mark": "Mark", "Luke": "Luke", "John": "John",
    "Acts": "Acts", "Romans": "Rom", "1 Corinthians": "1 Cor", "2 Corinthians": "2 Cor",
    "Galatians": "Gal", "Ephesians": "Eph", "Philippians": "Phil", "Colossians": "Col",
    "1 Thessalonians": "1 Thess", "2 Thessalonians": "2 Thess", "1 Timothy": "1 Tim",
    "2 Timothy": "2 Tim", "Titus": "Titus", "Philemon": "Phlm", "Hebrews": "Heb", "James": "Jas",
    "1 Peter": "1 Pet", "2 Peter": "2 Pet", "1 John": "1 John", "2 John": "2 John",
    "3 John": "3 John", "Jude": "Jude", "Revelation": "Rev",
}


def clean_name(name: str) -> str:
    name = re.sub(r"^III ", "3 ", re.sub(r"^II ", "2 ", re.sub(r"^I ", "1 ", name)))
    return "Revelation" if name == "Revelation of John" else name


def load_bible() -> list[tuple[str, list[int]]]:
    """[(book, [verse count per chapter]), ...] in canonical order."""
    if not KJV.exists():
        sys.exit(f"KJV data not found at {KJV}")
    books = json.loads(KJV.read_text())["books"]
    return [(clean_name(b["name"]), [len(c["verses"]) for c in b["chapters"]]) for b in books]


BIBLE = load_bible()
BOOK_INDEX = {name: i for i, (name, _) in enumerate(BIBLE)}
assert len(BIBLE) == 66, len(BIBLE)
assert sum(len(ch) for _, ch in BIBLE) == 1189
assert sum(len(ch) for _, ch in BIBLE[39:]) == 260
assert set(ABBR) == set(BOOK_INDEX), set(ABBR) ^ set(BOOK_INDEX)


def span_label(first: tuple[int, int], last: tuple[int, int], abbr: bool = True) -> str:
    """'Gen 1–3', 'Gen 50 – Exod 2', 'Ps 119' from (book index, chapter) pairs."""
    def bk(i: int, single: bool) -> str:
        n = BIBLE[i][0]
        if not abbr and n == "Psalms" and single:
            return "Psalm"
        return ABBR[n] if abbr else n

    (b1, c1), (b2, c2) = first, last
    one_chapter_book = lambda b: len(BIBLE[b][1]) == 1
    if b1 == b2:
        if c1 == c2:
            return bk(b1, True) if one_chapter_book(b1) else f"{bk(b1, True)} {c1}"
        return f"{bk(b1, False)} {c1}–{c2}"
    a = bk(b1, False) if one_chapter_book(b1) else f"{bk(b1, False)} {c1}"
    z = bk(b2, False) if one_chapter_book(b2) else f"{bk(b2, False)} {c2}"
    return f"{a} – {z}"


def chapters(books: range) -> list[tuple[int, int, int]]:
    """[(book index, chapter, verses), ...] for the given book indexes."""
    return [(b, c + 1, v) for b in books for c, v in enumerate(BIBLE[b][1])]


def whole_bible_plan() -> list[tuple[dt.date, str, list]]:
    """365 days; day boundaries fall where the running verse count crosses k/365 of the total."""
    chs = chapters(range(66))
    total = sum(v for *_, v in chs)
    days, cur, run, k = [], [], 0, 1
    for b, c, v in chs:
        cur.append((b, c))
        run += v
        if run >= total * k / 365 and k < 365:
            days.append(cur)
            cur, k = [], k + 1
    days.append(cur)
    assert len(days) == 365, len(days)
    flat = [x for d in days for x in d]
    assert len(flat) == 1189 and len(set(flat)) == 1189 and flat == [(b, c) for b, c, _ in chs]
    start = dt.date(YEAR, 1, 1)
    return [(start + dt.timedelta(i), span_label(d[0], d[-1]), d) for i, d in enumerate(days)]


def nt_plan() -> list[tuple[dt.date, str]]:
    """One New Testament chapter each weekday; 2027 has 261 weekdays, so the last is a catch-up day."""
    chs = chapters(range(39, 66))
    weekdays = [d for d in (dt.date(YEAR, 1, 1) + dt.timedelta(i) for i in range(365)) if d.weekday() < 5]
    assert len(chs) == 260 and len(weekdays) == 261
    plan = [(d, span_label((b, c), (b, c))) for d, (b, c, _) in zip(weekdays, chs)]
    plan.append((weekdays[-1], "Catch-up day"))
    return plan


REF = re.compile(r"^(?P<book>[1-3]? ?[A-Za-z ]+?) (?P<ch>\d+)(?::(?P<v1>\d+)(?:[–-](?P<v2>\d+))?)?$")


def check_ref(ref: str) -> str:
    """Raise unless the reference (e.g. 'Matthew 6:25–34', 'Psalm 23') exists in the KJV data."""
    m = REF.match(ref)
    assert m, ref
    book = {"Psalm": "Psalms"}.get(m["book"], m["book"])
    verses = BIBLE[BOOK_INDEX[book]][1]
    ch = int(m["ch"])
    assert 1 <= ch <= len(verses), ref
    for v in (m["v1"], m["v2"]):
        assert v is None or 1 <= int(v) <= verses[ch - 1], ref
    return ref


# Keep in sync with src/content/blog/soap-bible-study-method.mdx ("30-day SOAP plan for January").
SOAP_30 = [
    ("Psalm 1", "Two paths"), ("John 1:1–14", "The Word became flesh"), ("Lamentations 3:22–26", "New every morning"),
    ("Psalm 23", "The Lord is my shepherd"), ("Matthew 5:1–12", "The Beatitudes"), ("Proverbs 3:1–8", "Trust in the Lord"),
    ("John 3:16–21", "God so loved the world"), ("Matthew 6:25–34", "Do not worry"), ("Joshua 1:6–9", "Be strong and courageous"),
    ("Psalm 46", "Be still"), ("Romans 5:1–5", "Peace with God"), ("Isaiah 40:28–31", "Strength renewed"),
    ("John 15:1–8", "Abide in the vine"), ("Ephesians 2:4–10", "Saved by grace"), ("Philippians 4:4–9", "Peace that guards your heart"),
    ("Psalm 139:1–14", "Fully known"), ("Luke 15:11–24", "The lost son comes home"), ("James 1:2–8", "Ask for wisdom"),
    ("Romans 8:28–39", "Nothing can separate us"), ("Matthew 11:28–30", "Rest for the weary"), ("1 Corinthians 13:1–7", "What love is"),
    ("Galatians 5:16–25", "Fruit of the Spirit"), ("Micah 6:6–8", "What the Lord requires"), ("Colossians 3:12–17", "Put on love"),
    ("Hebrews 11:1–6", "Faith"), ("1 Peter 5:6–10", "Cast your cares"), ("Romans 12:1–2", "A renewed mind"),
    ("1 John 4:7–12", "God is love"), ("2 Corinthians 5:14–21", "A new creation"), ("Revelation 21:1–5", "All things new"),
]

# Keep in sync with src/content/blog/21-days-of-prayer-and-fasting.mdx (the 21-day prayer focus list).
FAST_21 = [
    ("Surrender and a clean heart", "Psalm 51:10–12"), ("Thanksgiving", "Psalm 100"), ("Hunger for God's Word", "Psalm 119:97–105"),
    ("Repentance", "1 John 1:5–9"), ("Your family", "Joshua 24:14–15"), ("Marriage and close relationships", "Colossians 3:12–14"),
    ("Your church and its leaders", "1 Thessalonians 5:12–18"), ("Wisdom for decisions", "James 1:5–6"), ("Provision and finances", "Philippians 4:10–19"),
    ("Health and healing", "James 5:13–16"), ("Work and calling", "Colossians 3:23–24"), ("Friends who don't know Jesus", "Romans 10:1–15"),
    ("Forgiveness", "Matthew 6:9–15"), ("Fear and anxiety", "Philippians 4:6–7"), ("Your city", "Jeremiah 29:7"),
    ("Your nation and its leaders", "1 Timothy 2:1–4"), ("The world and missions", "Matthew 28:18–20"), ("The next generation", "Psalm 78:1–7"),
    ("Using your gifts to serve", "1 Peter 4:8–11"), ("Unity in the church", "John 17:20–23"), ("What God has done; the year ahead", "Psalm 126"),
]

for ref, _ in SOAP_30:
    check_ref(ref)
for _, ref in FAST_21:
    check_ref(ref)
assert len(SOAP_30) == 30 and len(FAST_21) == 21


# ---------- drawing helpers ----------

def y(top: float) -> float:
    return H - top


def header(c: canvas.Canvas, title: str, subtitle: str) -> None:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(LEFT, y(64), title)
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 9)
    c.drawString(LEFT, y(81), subtitle)
    c.setFont("Helvetica", 8)
    c.drawRightString(RIGHT, y(64), "sermonkeeper.app")
    c.linkURL(SITE_URL, (RIGHT - 70, y(68), RIGHT, y(56)), relative=0)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(LEFT, y(94), RIGHT, y(94))


def footer(c: canvas.Canvas, label: str, page: int, pages: int) -> None:
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(W / 2, y(762), f"{label} from Sermon Keeper — sermonkeeper.app      Page {page} of {pages}")


def checkbox(c: canvas.Canvas, x: float, top: float, size: float = 7.5) -> None:
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.7)
    c.rect(x, y(top), size, size, stroke=1, fill=0)


def lines(c: canvas.Canvas, top: float, n: int, gap: float = 18, x0: float = LEFT, x1: float = RIGHT) -> float:
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    for i in range(n):
        c.line(x0, y(top + i * gap), x1, y(top + i * gap))
    return top + n * gap


def app_box(c: canvas.Canvas, box_top: float, url: str, title: str, text: list[str], box_h: float = 104) -> None:
    c.setFillColor(TINT)
    c.roundRect(LEFT, y(box_top + box_h), RIGHT - LEFT, box_h, 10, stroke=0, fill=1)
    qr_size = box_h - 24
    qr = QrCodeWidget(url)
    x0, y0, x1, y1 = qr.getBounds()
    d = Drawing(qr_size, qr_size, transform=[qr_size / (x1 - x0), 0, 0, qr_size / (y1 - y0), 0, 0])
    d.add(qr)
    qr_x, qr_y = LEFT + 12, y(box_top + 12 + qr_size)
    renderPDF.draw(d, c, qr_x, qr_y)
    c.linkURL(url, (qr_x, qr_y, qr_x + qr_size, qr_y + qr_size), relative=0)
    tx = qr_x + qr_size + 16
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(tx, y(box_top + 27), title)
    c.setFillColor(INK)
    c.setFont("Helvetica", 9)
    for i, line in enumerate(text):
        c.drawString(tx, y(box_top + 44 + i * 12.5), line)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    cta = "Scan the code, or tap here: free 3-day trial on the App Store →"
    ty = box_top + box_h - 12
    c.drawString(tx, y(ty), cta)
    c.linkURL(url, (tx, y(ty + 3), tx + c.stringWidth(cta, "Helvetica-Bold", 9), y(ty - 9)), relative=0)


def month_columns(c: canvas.Canvas, months: list[int], rows: dict[int, list[tuple[str, str]]], top: float, row_h: float) -> None:
    col_w = (RIGHT - LEFT - 2 * 14) / 3
    for i, m in enumerate(months):
        x = LEFT + i * (col_w + 14)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y(top), dt.date(YEAR, m, 1).strftime("%B"))
        t = top + 17
        for date_label, reading in rows[m]:
            checkbox(c, x, t + 1.5)
            c.setFillColor(GRAY)
            c.setFont("Helvetica", 7.5)
            c.drawString(x + 11, y(t), date_label)
            c.setFillColor(INK)
            c.setFont("Helvetica", 8.5)
            c.drawString(x + 44, y(t), reading)
            t += row_h


# ---------- PDFs ----------

def build_whole_bible() -> None:
    plan = whole_bible_plan()
    rows: dict[int, list] = {m: [] for m in range(1, 13)}
    for d, label, _ in plan:
        rows[d.month].append((d.strftime("%a %-d"), label))
    url = app_url("landing_blog_reading_plan_2027_pdf")
    c = canvas.Canvas(str(DOWNLOADS / "bible-reading-plan-2027.pdf"), pagesize=(W, H))
    c.setTitle(f"Bible Reading Plan {YEAR}: The Whole Bible in a Year")
    c.setAuthor("Sermon Keeper")
    c.setSubject("Read the whole Bible in 365 days, in canonical order")
    for p in range(4):
        header(c, f"Bible in a Year {YEAR}", "All 1,189 chapters, Genesis to Revelation, about 85 verses (10–15 minutes) a day. Tick each day as you go.")
        month_columns(c, [3 * p + 1, 3 * p + 2, 3 * p + 3], rows, 122, 15.4)
        if p == 3:
            app_box(c, 648, url, "Take notes on what you read", [
                "In Sermon Keeper, scan a Bible page and pick a verse: you get a SOAP",
                "study card with observation, application, cross-references and a prayer.",
                "It also records Sunday's sermon and lists every verse the pastor named.",
            ])
        footer(c, "Free Bible reading plan", p + 1, 4)
        c.showPage()
    c.save()


def build_nt() -> None:
    plan = nt_plan()
    rows: dict[int, list] = {m: [] for m in range(1, 13)}
    for d, label in plan:
        rows[d.month].append((d.strftime("%a %-d"), label))
    url = app_url("landing_blog_reading_plan_2027_nt_pdf")
    c = canvas.Canvas(str(DOWNLOADS / "new-testament-reading-plan-2027.pdf"), pagesize=(W, H))
    c.setTitle(f"New Testament Reading Plan {YEAR}: One Chapter a Weekday")
    c.setAuthor("Sermon Keeper")
    c.setSubject("Read the New Testament in a year, one chapter each weekday")
    for p in range(2):
        header(c, f"New Testament in a Year {YEAR}", "All 260 chapters, one a day, Monday to Friday. Weekends are free for church and catching up.")
        month_columns(c, list(range(6 * p + 1, 6 * p + 4)), rows, 122, 12.2)
        month_columns(c, list(range(6 * p + 4, 6 * p + 7)), rows, 122 + 17 + 23 * 12.2 + 16, 12.2)
        footer(c, "Free New Testament reading plan", p + 1, 3)
        c.showPage()
    header(c, f"New Testament in a Year {YEAR}", "How to use this plan")
    t = 130
    c.setFillColor(INK)
    c.setFont("Helvetica", 10.5)
    for line in [
        "• Read one chapter each weekday. Most take about five minutes.",
        "• Fell behind? Skip ahead to today's date and use a weekend to catch up. Don't restart.",
        "• Write one verse that stood out and one thing you'll do. That's enough.",
        "• On Sunday, listen for how the sermon connects with what you read this week.",
        "• December 31 is a catch-up day: the plan finishes Revelation 22 on December 30.",
    ]:
        c.drawString(LEFT, y(t), line)
        t += 20
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(LEFT, y(t + 16), "Notes")
    lines(c, t + 40, 18)
    app_box(c, 648, url, "Keep your Sunday notes with your reading", [
        "Sermon Keeper records the sermon while you tap short notes, then gives",
        "you a transcript and a summary with every verse the pastor named.",
        "Scan a Bible page to get a SOAP study card for any verse.",
    ])
    footer(c, "Free New Testament reading plan", 3, 3)
    c.showPage()
    c.save()


def build_fasting() -> None:
    url = app_url("landing_blog_fasting_21_pdf")
    pages = 8
    c = canvas.Canvas(str(DOWNLOADS / "21-day-prayer-fasting-journal.pdf"), pagesize=(W, H))
    c.setTitle("21 Days of Prayer and Fasting Journal")
    c.setAuthor("Sermon Keeper")
    c.setSubject("A printable 21-day prayer and fasting journal")
    header(c, "21 Days of Prayer & Fasting", "My plan. Fill this in before day 1, and come back to it on day 21.")
    t = 128
    for label, n in [
        ("Start date", 1), ("The kind of fast I'm doing (and what I'm setting aside)", 2),
        ("Why I'm fasting: what I want to seek God about", 3), ("People I'm praying for by name", 3),
        ("When I'll pray each day, and where", 1), ("What I'll do instead (with the time, the meal, the scrolling)", 2),
    ]:
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(LEFT, y(t), label)
        t = lines(c, t + 20, n) + 10
    c.setFillColor(GRAY)
    c.setFont("Helvetica-Oblique", 8.5)
    c.drawString(LEFT, y(t + 2), "Talk to your doctor before fasting from food, especially if you have a health condition, are pregnant or take medication.")
    app_box(c, 648, url, "Extra services during the fast?", [
        "Sermon Keeper records each message while you tap short notes, then gives",
        "you a transcript and a summary with every verse named. Scan a Bible page",
        "to get a SOAP study card for today's reading.",
    ])
    footer(c, "Free 21-day prayer and fasting journal", 1, pages)
    c.showPage()
    for p in range(7):
        header(c, "21 Days of Prayer & Fasting", "Read the passage, pray about the focus, write a few lines. Five minutes is enough.")
        t = 116
        for day in range(3 * p + 1, 3 * p + 4):
            focus, ref = FAST_21[day - 1]
            c.setFillColor(NAVY)
            c.setFont("Helvetica-Bold", 13)
            c.drawString(LEFT, y(t + 12), f"Day {day}")
            c.setFont("Helvetica", 8.5)
            c.setFillColor(GRAY)
            c.drawRightString(RIGHT, y(t + 12), "Date  ______________")
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(LEFT + 52, y(t + 12), focus)
            c.setFont("Helvetica", 9.5)
            c.drawString(LEFT + 52 + c.stringWidth(focus, "Helvetica-Bold", 10) + 8, y(t + 12), f"· Read {ref}")
            c.setFillColor(GRAY)
            c.setFont("Helvetica", 8.5)
            c.drawString(LEFT, y(t + 34), "What stood out / what I sense God saying")
            tt = lines(c, t + 52, 3, 17)
            c.drawString(LEFT, y(tt + 4), "My prayer")
            tt = lines(c, tt + 22, 2, 17)
            checkbox(c, LEFT, tt + 8)
            c.setFont("Helvetica", 8.5)
            c.drawString(LEFT + 12, y(tt + 8), "Kept my fast today")
            checkbox(c, LEFT + 120, tt + 8)
            c.drawString(LEFT + 132, y(tt + 8), "Adjusted it, and that's okay")
            t = tt + 30
        footer(c, "Free 21-day prayer and fasting journal", p + 2, pages)
        c.showPage()
    c.save()


def build_soap_30() -> None:
    url = app_url("landing_blog_soap_jan_pdf")
    c = canvas.Canvas(str(DOWNLOADS / "soap-30-day-plan-january.pdf"), pagesize=(W, H))
    c.setTitle("30-Day SOAP Bible Study Plan for January")
    c.setAuthor("Sermon Keeper")
    c.setSubject("30 beginner-friendly passages for SOAP Bible study")
    header(c, "30-Day SOAP Plan for January", "One short passage a day. Write: Scripture, Observation, Application, Prayer. About 10 minutes.")
    t = 120
    col_w = (RIGHT - LEFT - 20) / 2
    for i, (ref, theme) in enumerate(SOAP_30):
        x = LEFT + (i // 15) * (col_w + 20)
        tt = t + (i % 15) * 31
        checkbox(c, x, tt + 1.5, 9)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 8)
        c.drawString(x + 14, y(tt), f"Jan {i + 1}")
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 50, y(tt), ref)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 8.5)
        c.drawString(x + 50, y(tt + 12), theme)
    t += 15 * 31 + 2
    for k, (letter, text) in enumerate([
        ("S", "Scripture: copy the verse that stands out."), ("O", "Observation: what does it say? What do you notice?"),
        ("A", "Application: what will you do today?"), ("P", "Prayer: pray it back to God."),
    ]):
        x = LEFT + (k % 2) * (col_w + 20)
        tt = t + (k // 2) * 15
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y(tt), letter)
        c.setFillColor(INK)
        c.setFont("Helvetica", 8.5)
        c.drawString(x + 13, y(tt), text)
    app_box(c, 648, url, "Do SOAP on your phone", [
        "In Sermon Keeper, scan today's Bible page and pick a verse: you get a SOAP",
        "study card with observation, application, cross-references and a prayer",
        "in about 30 seconds. Then write your own in the margin of this page.",
    ])
    footer(c, "Free 30-day SOAP plan", 1, 1)
    c.showPage()
    c.save()


if __name__ == "__main__":
    build_whole_bible()
    build_nt()
    build_fasting()
    build_soap_30()
    plan = whole_bible_plan()
    print("whole Bible:", len(plan), "days,", sum(len(d) for *_, d in plan), "chapters; Dec 31 =", plan[-1][1])
    nt = nt_plan()
    print("NT:", len(nt) - 1, "chapters on", len(nt), "weekdays; last reading", nt[-2][0], nt[-2][1])
    print("SOAP 30 and 21-day refs checked against KJV")
