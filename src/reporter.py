import os
from datetime import date

from fpdf import FPDF

REPORTS_DIR = "reports"
FONT_REGULAR = os.path.join("assets", "NotoSans-Regular.ttf")
FONT_BOLD = os.path.join("assets", "NotoSans-Bold.ttf")


def save_report(ticker: str, analysis: str) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filename = os.path.join(REPORTS_DIR, f"raport_{ticker}_{date.today()}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"RAPORT INWESTYCYJNY — {ticker}\n")
        f.write(f"Data: {date.today().strftime('%d.%m.%Y')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(analysis)
    return filename


def list_reports() -> list[str]:
    if not os.path.isdir(REPORTS_DIR):
        return []
    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".txt")]
    return sorted(files, reverse=True)


def load_report(filename: str) -> str:
    path = os.path.join(REPORTS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def generate_pdf(ticker: str, analysis: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("NotoSans", "", FONT_REGULAR)
    pdf.add_font("NotoSans", "B", FONT_BOLD)

    pdf.set_font("NotoSans", "B", 16)
    pdf.cell(0, 10, f"RAPORT INWESTYCYJNY — {ticker}", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("NotoSans", "", 11)
    pdf.cell(0, 8, f"Data: {date.today().strftime('%d.%m.%Y')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.set_font("NotoSans", "", 11)
    pdf.multi_cell(0, 7, analysis)

    return bytes(pdf.output())
