from datetime import date


def save_report(ticker: str, analysis: str) -> str:
    filename = f"raport_{ticker}_{date.today()}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"RAPORT INWESTYCYJNY — {ticker}\n")
        f.write(f"Data: {date.today()}\n")
        f.write("=" * 60 + "\n\n")
        f.write(analysis)
    return filename
