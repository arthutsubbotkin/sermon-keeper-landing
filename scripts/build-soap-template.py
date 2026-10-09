"""Build public/downloads/soap-bible-study-template.pdf.

One printable page: the four SOAP sections with writing lines, and at the
bottom a QR code + link to Sermon Keeper on the App Store, tagged
ct=landing_blog_soap_pdf so installs from the printed / saved template show
up in App Store Connect's campaign report.

Run:  python3 scripts/build-soap-template.py
"""
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent.parent / "public/downloads/soap-bible-study-template.pdf"
APP_URL = "https://apps.apple.com/app/apple-store/id6758739935?pt=128512327&ct=landing_blog_soap_pdf&mt=8"
SITE_URL = "https://sermonkeeper.app"

W, H = 612, 792
LEFT, RIGHT = 65, 547
NAVY = HexColor("#0C2882")
GRAY = HexColor("#6B7280")
RULE = HexColor("#CBD5E1")
TINT = HexColor("#EFF6FF")


def y(top: float) -> float:
    """Convert a distance from the top of the page to ReportLab's bottom-up y."""
    return H - top


def build() -> None:
    c = canvas.Canvas(str(OUT), pagesize=(W, H))
    c.setTitle("SOAP Bible Study Template")
    c.setAuthor("Sermon Keeper")
    c.setSubject("Scripture, Observation, Application, Prayer")

    # Header
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(LEFT, y(72), "SOAP Bible Study")
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 9)
    c.drawString(LEFT, y(89), "Scripture  ·  Observation  ·  Application  ·  Prayer")
    c.setFont("Helvetica", 8)
    c.drawRightString(RIGHT, y(72), "sermonkeeper.app")
    c.linkURL(SITE_URL, (RIGHT - 70, y(76), RIGHT, y(64)), relative=0)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(LEFT, y(104), RIGHT, y(104))

    # Date / passage
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(LEFT, y(133), "Date:")
    c.drawString(288, y(133), "Passage:")
    c.setStrokeColor(GRAY)
    c.line(98, y(134), 208, y(134))
    c.line(341, y(134), 477, y(134))

    # The four sections
    sections = [
        ("S", "Scripture", "Write out the verse or passage that stood out to you."),
        ("O", "Observation", "What is happening here? What does it show you about God?"),
        ("A", "Application", "What is one way this changes how you live this week?"),
        ("P", "Prayer", "Pray the passage back to God in your own words."),
    ]
    top = 173
    for letter, name, hint in sections:
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(LEFT, y(top), f"{letter}  —  {name}")
        c.setFillColor(GRAY)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(LEFT, y(top + 14), hint)
        c.setStrokeColor(RULE)
        for off in (37, 59, 80):
            c.line(LEFT, y(top + off), RIGHT, y(top + off))
        top += 106

    # App box with QR code
    box_top, box_h = 603, 112
    c.setFillColor(TINT)
    c.setStrokeColor(TINT)
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
    c.drawString(tx, y(box_top + 30), "Skip the copying next time")
    c.setFillColor(HexColor("#1F2937"))
    c.setFont("Helvetica", 9.5)
    lines = [
        "Point Sermon Keeper at your Bible page and it fills in a SOAP card",
        "for you in about 30 seconds: the verse, an observation, an application",
        "and a short prayer. It records and transcribes your Sunday sermon too.",
    ]
    for i, line in enumerate(lines):
        c.drawString(tx, y(box_top + 48 + i * 13), line)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9.5)
    cta = "Scan the code, or tap here: free 3-day trial on the App Store →"
    c.drawString(tx, y(box_top + 96), cta)
    c.linkURL(APP_URL, (tx, y(box_top + 99), tx + c.stringWidth(cta, "Helvetica-Bold", 9.5), y(box_top + 88)), relative=0)

    # Footer
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 7.5)
    footer = "Free SOAP template from Sermon Keeper — record, transcribe, and study every sermon.  sermonkeeper.app"
    c.drawCentredString(W / 2, y(752), footer)
    fw = c.stringWidth(footer, "Helvetica", 7.5)
    c.linkURL(SITE_URL, (W / 2 - fw / 2, y(755), W / 2 + fw / 2, y(745)), relative=0)

    c.showPage()
    c.save()


if __name__ == "__main__":
    build()
    print(f"wrote {OUT}")
