"""Build public/downloads/sermon-notes-template.pdf.

Two printable pages for taking notes during a sermon: date, speaker, title and
Scripture, three main points, key verse, questions, application and prayer.
Page 2 ends with a QR code + link to Sermon Keeper on the App Store, tagged
ct=landing_blog_take_notes_pdf so installs from the template show up in App
Store Connect's campaign report.

Run:  python3 scripts/build-sermon-notes-template.py
"""
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent.parent / "public/downloads/sermon-notes-template.pdf"
APP_URL = "https://apps.apple.com/app/apple-store/id6758739935?pt=128512327&ct=landing_blog_take_notes_pdf&mt=8"
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


def header(c: canvas.Canvas, subtitle: str) -> None:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(LEFT, y(72), "Sermon Notes")
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


def section(c: canvas.Canvas, title: str, hint: str, top: float, lines: int, gap: float = 22) -> float:
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(LEFT, y(top), title)
    c.setFillColor(GRAY)
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(LEFT, y(top + 14), hint)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    for i in range(lines):
        ly = top + 37 + i * gap
        c.line(LEFT, y(ly), RIGHT, y(ly))
    return top + 37 + (lines - 1) * gap


def footer(c: canvas.Canvas, page: int) -> None:
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 7.5)
    text = f"Free sermon notes template from Sermon Keeper — sermonkeeper.app      Page {page} of 2"
    c.drawCentredString(W / 2, y(752), text)
    tw = c.stringWidth(text, "Helvetica", 7.5)
    c.linkURL(SITE_URL, (W / 2 - tw / 2, y(755), W / 2 + tw / 2, y(745)), relative=0)


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

    box_top, box_h = 618, 112
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
    c.drawString(tx, y(box_top + 30), "Rather record it on your phone?")
    c.setFillColor(INK)
    c.setFont("Helvetica", 9.5)
    for i, line in enumerate([
        "Sermon Keeper records the sermon while you tap in short notes, each",
        "saved at the moment you wrote it. When the service ends you get a",
        "transcript and a summary with the main points and every verse named.",
    ]):
        c.drawString(tx, y(box_top + 48 + i * 13), line)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9.5)
    cta = "Scan the code, or tap here: free 3-day trial on the App Store →"
    c.drawString(tx, y(box_top + 96), cta)
    c.linkURL(APP_URL, (tx, y(box_top + 99), tx + c.stringWidth(cta, "Helvetica-Bold", 9.5), y(box_top + 88)), relative=0)
    footer(c, 2)
    c.showPage()
    c.save()


if __name__ == "__main__":
    build()
    print(f"wrote {OUT}")
