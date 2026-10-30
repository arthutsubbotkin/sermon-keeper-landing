"""Build the three printable sermon notes templates in public/downloads/.

- sermon-notes-template.pdf: two pages: date, speaker, title and Scripture,
  three main points, then key verse, questions, application and prayer.
  ct=landing_blog_take_notes_pdf.
- sermon-notes-template-one-page.pdf: the same essentials on one page.
  ct=landing_blog_sermon_template_one_page_pdf.
- sermon-notes-template-kids.pdf: one page for children, with a drawing box
  and a word tally. ct=landing_blog_sermon_template_kids_pdf.

Each ends with a QR code + link to Sermon Keeper on the App Store, tagged with
its own ct so installs from each template show up separately in App Store
Connect's campaign report.

Run:  python3 scripts/build-sermon-notes-template.py
"""
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

DOWNLOADS = Path(__file__).resolve().parent.parent / "public/downloads"
OUT = DOWNLOADS / "sermon-notes-template.pdf"
OUT_ONE_PAGE = DOWNLOADS / "sermon-notes-template-one-page.pdf"
OUT_KIDS = DOWNLOADS / "sermon-notes-template-kids.pdf"


def app_url(ct: str) -> str:
    return f"https://apps.apple.com/app/apple-store/id6758739935?pt=128512327&ct={ct}&mt=8"


APP_URL = app_url("landing_blog_take_notes_pdf")
SITE_URL = "https://sermonkeeper.app"

W, H = 612, 792
LEFT, RIGHT = 65, 547
NAVY = HexColor("#0C2882")
GRAY = HexColor("#6B7280")
RULE = HexColor("#CBD5E1")
TINT = HexColor("#EFF6FF")
INK = HexColor("#1F2937")


def y(top: float) -> float:
    return H - top


def header(c: canvas.Canvas, subtitle: str, title: str = "Sermon Notes") -> None:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(LEFT, y(72), title)
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 9)
    c.drawString(LEFT, y(89), subtitle)
    c.setFont("Helvetica", 8)
    c.drawRightString(RIGHT, y(72), "sermonkeeper.app")
    c.linkURL(SITE_URL, (RIGHT - 70, y(76), RIGHT, y(64)), relative=0)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(LEFT, y(104), RIGHT, y(104))


def field(c: canvas.Canvas, label: str, x: float, top: float, x_end: float) -> None:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x, y(top), label)
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.6)
    c.line(x + c.stringWidth(label, "Helvetica-Bold", 9) + 8, y(top + 1), x_end, y(top + 1))


def section(c: canvas.Canvas, title: str, hint: str, top: float, lines: int, gap: float = 22,
            x0: float = LEFT, x1: float = RIGHT) -> float:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x0, y(top), title)
    c.setFillColor(GRAY)
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(x0, y(top + 14), hint)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    for i in range(lines):
        ly = top + 37 + i * gap
        c.line(x0, y(ly), x1, y(ly))
    return top + 37 + (lines - 1) * gap


def footer(c: canvas.Canvas, page: int, pages: int = 2) -> None:
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 7.5)
    text = "Free sermon notes template from Sermon Keeper — sermonkeeper.app"
    if pages > 1:
        text += f"      Page {page} of {pages}"
    c.drawCentredString(W / 2, y(752), text)
    tw = c.stringWidth(text, "Helvetica", 7.5)
    c.linkURL(SITE_URL, (W / 2 - tw / 2, y(755), W / 2 + tw / 2, y(745)), relative=0)


def app_box(c: canvas.Canvas, box_top: float, url: str, title: str = "Rather record it on your phone?",
            lines: tuple[str, ...] = (
                "Sermon Keeper records the sermon while you tap in short notes, each",
                "saved at the moment you wrote it. When the service ends you get a",
                "transcript and a summary with the main points and every verse named.",
            )) -> None:
    box_h = 112
    c.setFillColor(TINT)
    c.roundRect(LEFT, y(box_top + box_h), RIGHT - LEFT, box_h, 10, stroke=0, fill=1)
    qr_size = 84
    qr = QrCodeWidget(url)
    x0, y0, x1, y1 = qr.getBounds()
    d = Drawing(qr_size, qr_size, transform=[qr_size / (x1 - x0), 0, 0, qr_size / (y1 - y0), 0, 0])
    d.add(qr)
    qr_x, qr_y = LEFT + 14, y(box_top + 14 + qr_size)
    renderPDF.draw(d, c, qr_x, qr_y)
    c.linkURL(url, (qr_x, qr_y, qr_x + qr_size, qr_y + qr_size), relative=0)

    tx = qr_x + qr_size + 18
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(tx, y(box_top + 30), title)
    c.setFillColor(INK)
    c.setFont("Helvetica", 9.5)
    for i, line in enumerate(lines):
        c.drawString(tx, y(box_top + 48 + i * 13), line)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9.5)
    cta = "Scan the code, or tap here: free 3-day trial on the App Store →"
    c.drawString(tx, y(box_top + 96), cta)
    c.linkURL(url, (tx, y(box_top + 99), tx + c.stringWidth(cta, "Helvetica-Bold", 9.5), y(box_top + 88)), relative=0)


def build() -> None:
    c = canvas.Canvas(str(OUT), pagesize=(W, H))
    c.setTitle("Sermon Notes Template")
    c.setAuthor("Sermon Keeper")
    c.setSubject("Printable sermon notes template")

    # Page 1: the sermon itself
    header(c, "Date  ·  Speaker  ·  Scripture  ·  Main points  ·  Key verse  ·  Application  ·  Prayer")
    field(c, "Date:", LEFT, 132, 250)
    field(c, "Speaker:", 288, 132, RIGHT)
    field(c, "Sermon title:", LEFT, 160, RIGHT)
    field(c, "Scripture:", LEFT, 188, RIGHT)

    top = 228
    for n in (1, 2, 3):
        end = section(
            c,
            f"Main point {n}",
            "The point in a few words, then the verse, story or example that went with it.",
            top,
            lines=5,
        )
        top = end + 34
    footer(c, 1)
    c.showPage()

    # Page 2: what you take home
    header(c, "Key verse  ·  Questions  ·  Application  ·  Prayer")
    top = 140
    top = section(c, "Key verse", "The one verse you want to remember. Write it out in full.", top, lines=3) + 34
    top = section(c, "Questions", "Anything you didn't understand, or want to look up later.", top, lines=3) + 34
    top = section(c, "Application", "One thing you will do this week because of this sermon. Be specific.", top, lines=3) + 34
    section(c, "Prayer", "Pray the message back to God in your own words.", top, lines=3)

    app_box(c, 618, APP_URL)
    footer(c, 2)
    c.showPage()
    c.save()


def build_one_page() -> None:
    c = canvas.Canvas(str(OUT_ONE_PAGE), pagesize=(W, H))
    c.setTitle("Sermon Notes Template (One Page)")
    c.setAuthor("Sermon Keeper")
    c.setSubject("Printable one-page sermon notes template")

    header(c, "Date  ·  Speaker  ·  Scripture  ·  Main points  ·  Key verse  ·  This week")
    field(c, "Date:", LEFT, 130, 250)
    field(c, "Speaker:", 288, 130, RIGHT)
    field(c, "Sermon title:", LEFT, 156, RIGHT)
    field(c, "Scripture:", LEFT, 182, RIGHT)

    top = 216
    for n in (1, 2, 3):
        top = section(c, f"Main point {n}", "The point in a few words, and the verse or story that went with it.",
                      top, lines=3, gap=20) + 26
    mid = (LEFT + RIGHT) / 2
    section(c, "Key verse", "The one verse you want to remember.", top, lines=2, gap=20, x1=mid - 14)
    section(c, "This week I will…", "One specific thing to do.", top, lines=2, gap=20, x0=mid + 14)
    app_box(c, 628, app_url("landing_blog_sermon_template_one_page_pdf"))
    footer(c, 1, pages=1)
    c.showPage()
    c.save()


def tally(c: canvas.Canvas, words: list[str], top: float) -> None:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(LEFT, y(top), "Word hunt")
    c.setFillColor(GRAY)
    c.setFont("Helvetica-Oblique", 8.5)
    c.drawString(LEFT, y(top + 14), "Make a mark every time you hear one of these words.")
    col_w = (RIGHT - LEFT) / len(words)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.8)
    for i, word in enumerate(words):
        x = LEFT + i * col_w
        c.roundRect(x + 4, y(top + 76), col_w - 8, 52, 8, stroke=1, fill=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x + col_w / 2, y(top + 40), word)


def build_kids() -> None:
    c = canvas.Canvas(str(OUT_KIDS), pagesize=(W, H))
    c.setTitle("Sermon Notes for Kids")
    c.setAuthor("Sermon Keeper")
    c.setSubject("Printable sermon notes page for children")

    header(c, "Listen, draw and write: one page for each Sunday", title="My Sermon Notes")
    field(c, "My name:", LEFT, 130, 300)
    field(c, "Date:", 330, 130, RIGHT)
    field(c, "The Bible story or verse:", LEFT, 158, RIGHT)

    tally(c, ["God", "Jesus", "Love", "Pray", "Bible"], 196)

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(LEFT, y(300), "Draw what the sermon was about")
    c.setStrokeColor(RULE)
    c.setLineWidth(0.8)
    c.roundRect(LEFT, y(470), RIGHT - LEFT, 156, 10, stroke=1, fill=0)

    top = section(c, "One thing I learned about God", "Write it, or ask a grown-up to help.", 500, lines=2, gap=22) + 30
    section(c, "This week I will…", "Something kind or brave you can do.", top, lines=1)

    app_box(c, 628, app_url("landing_blog_sermon_template_kids_pdf"), title="For parents",
            lines=(
                "Sermon Keeper records the sermon on your iPhone and gives you a",
                "transcript and a summary afterwards, so you can talk about it",
                "together at lunch even if you spent the service with the kids.",
            ))
    footer(c, 1, pages=1)
    c.showPage()
    c.save()


if __name__ == "__main__":
    build()
    build_one_page()
    build_kids()
    for out in (OUT, OUT_ONE_PAGE, OUT_KIDS):
        print(f"wrote {out}")
