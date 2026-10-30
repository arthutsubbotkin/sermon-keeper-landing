"""Build public/downloads/bible-journal-prompts.pdf.

Forty Bible journal prompts in six themes on two printable pages, the same
list as the "Bible Journaling for Beginners" post. Page 2 ends with a QR code +
link to Sermon Keeper on the App Store, tagged
ct=landing_blog_bible_journaling_pdf so installs from the printable show up in
App Store Connect's campaign report.

Run:  python3 scripts/build-bible-journal-prompts.py
"""
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent.parent / "public/downloads/bible-journal-prompts.pdf"
APP_URL = "https://apps.apple.com/app/apple-store/id6758739935?pt=128512327&ct=landing_blog_bible_journaling_pdf&mt=8"
SITE_URL = "https://sermonkeeper.app"

W, H = 612, 792
LEFT, RIGHT = 60, 552
NAVY = HexColor("#0C2882")
GRAY = HexColor("#6B7280")
RULE = HexColor("#CBD5E1")
TINT = HexColor("#EFF6FF")
INK = HexColor("#1F2937")

# Keep in sync with the prompt list in src/content/blog/bible-journaling-for-beginners.mdx.
THEMES = [
    ("Any passage", [
        "What does this passage show me about God?",
        "What does it show me about people, and about me?",
        "Is there a promise here I can hold on to?",
        "Is there a command here I need to obey?",
        "Which word or phrase stood out, and why?",
        "What question would I ask the writer if I could?",
        "How would I explain this passage to a friend in two sentences?",
    ]),
    ("Gratitude", [
        "Where did I see God's kindness in the last 24 hours?",
        "Lamentations 3:22–23: what mercy is \"new every morning\" for me today?",
        "Psalm 23:1: what do I have that I once prayed for?",
        "Who has God put in my life this year, and how can I thank them?",
        "Write about an answered prayer you almost forgot.",
        "What is one ordinary thing I am grateful for today?",
    ]),
    ("Worry and peace", [
        "Philippians 4:6–7: what am I anxious about? Write it as a prayer.",
        "Isaiah 26:3: what has my mind been \"stayed on\" this week?",
        "Psalm 46:10: where do I need to be still instead of fixing it?",
        "Matthew 11:28: what is making me \"heavy laden\" right now?",
        "What would I do differently today if I trusted God fully?",
        "Proverbs 3:5–6: where am I leaning on my own understanding?",
        "Psalm 34:18: where do I need God to be near?",
    ]),
    ("Who God says I am", [
        "2 Corinthians 5:17: what \"old things\" am I still carrying?",
        "Ephesians 2:10: what good work might God have prepared for me?",
        "John 15:5: what does \"abiding\" look like in my ordinary day?",
        "Exodus 3:11: where do I feel like Moses, asking \"Who am I?\"",
        "Galatians 5:22–23: which fruit of the Spirit do I most want to grow?",
        "1 John 1:9: is there anything I need to confess and let go?",
    ]),
    ("Prayer and listening", [
        "Psalm 139:23–24: ask God to search your heart. What comes up?",
        "1 Samuel 3:10: if I said \"Speak, Lord,\" what might he say?",
        "1 Kings 19:12: where might God be speaking quietly, not loudly?",
        "Write a prayer using the exact words of today's verse.",
        "Who can I pray for by name this week, and what do they need?",
        "Mark 1:35: when and where can I be alone with God this week?",
    ]),
    ("Living it out", [
        "James 1:22: what have I heard but not yet done?",
        "Micah 6:8: where can I do justly or love mercy this week?",
        "Matthew 6:33: what does seeking God first look like in my schedule?",
        "Genesis 50:20: where might God bring good out of something hard?",
        "What was the main point of Sunday's sermon, in one sentence?",
        "What did the sermon ask me to do, and when will I do it?",
        "Luke 2:19: what is God asking me to \"ponder\" rather than rush past?",
        "What will I do differently tomorrow because of what I read today?",
    ]),
]


def y(top: float) -> float:
    return H - top


def header(c: canvas.Canvas, subtitle: str) -> None:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(LEFT, y(70), "Bible Journal Prompts")
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 9)
    c.drawString(LEFT, y(87), subtitle)
    c.setFont("Helvetica", 8)
    c.drawRightString(RIGHT, y(70), "sermonkeeper.app")
    c.linkURL(SITE_URL, (RIGHT - 70, y(74), RIGHT, y(62)), relative=0)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(LEFT, y(100), RIGHT, y(100))


def footer(c: canvas.Canvas, page: int) -> None:
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 7.5)
    text = f"Free Bible journal prompts from Sermon Keeper — sermonkeeper.app      Page {page} of 2"
    c.drawCentredString(W / 2, y(756), text)


def theme(c: canvas.Canvas, title: str, prompts: list[str], top: float, start: int) -> float:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(LEFT, y(top), title)
    top += 20
    for i, p in enumerate(prompts):
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawRightString(LEFT + 18, y(top), f"{start + i}.")
        c.setFillColor(INK)
        c.setFont("Helvetica", 10)
        c.drawString(LEFT + 24, y(top), p)
        top += 17
    return top + 14


def app_box(c: canvas.Canvas, box_top: float) -> None:
    box_h = 112
    c.setFillColor(TINT)
    c.roundRect(LEFT, y(box_top + box_h), RIGHT - LEFT, box_h, 10, stroke=0, fill=1)
    qr_size = 84
    qr = QrCodeWidget(APP_URL)
    x0, y0, x1, y1 = qr.getBounds()
    d = Drawing(qr_size, qr_size, transform=[qr_size / (x1 - x0), 0, 0, qr_size / (y1 - y0), 0, 0])
    d.add(qr)
    qr_x, qr_y = LEFT + 14, y(box_top + 14 + qr_size)
    renderPDF.draw(d, c, qr_x, qr_y)
    c.linkURL(APP_URL, (qr_x, qr_y, qr_x + qr_size, qr_y + qr_size), relative=0)
    tx = qr_x + qr_size + 18
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(tx, y(box_top + 30), "Journal on your phone?")
    c.setFillColor(INK)
    c.setFont("Helvetica", 9.5)
    for i, line in enumerate([
        "In Sermon Keeper, scan a Bible page and pick a verse: you get a SOAP",
        "study card with observation, application, cross-references and a",
        "prayer. It also records Sunday's sermon and lists every verse named.",
    ]):
        c.drawString(tx, y(box_top + 48 + i * 13), line)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9.5)
    cta = "Scan the code, or tap here: free 3-day trial on the App Store →"
    c.drawString(tx, y(box_top + 96), cta)
    c.linkURL(APP_URL, (tx, y(box_top + 99), tx + c.stringWidth(cta, "Helvetica-Bold", 9.5), y(box_top + 88)), relative=0)


def build() -> None:
    c = canvas.Canvas(str(OUT), pagesize=(W, H))
    c.setTitle("Bible Journal Prompts")
    c.setAuthor("Sermon Keeper")
    c.setSubject("40 printable Bible journal prompts")

    header(c, "Pick one prompt, read the verse in your Bible, and write for five minutes.")
    top, n = 130, 1
    for title, prompts in THEMES[:3]:
        top = theme(c, title, prompts, top, n)
        n += len(prompts)
    footer(c, 1)
    c.showPage()

    header(c, "Pick one prompt, read the verse in your Bible, and write for five minutes.")
    top = 130
    for title, prompts in THEMES[3:]:
        top = theme(c, title, prompts, top, n)
        n += len(prompts)
    app_box(c, 628)
    footer(c, 2)
    c.showPage()
    c.save()


if __name__ == "__main__":
    build()
    print(f"wrote {OUT}")
    print(sum(len(p) for _, p in THEMES), "prompts")
