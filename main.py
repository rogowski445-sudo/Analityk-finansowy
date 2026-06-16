from dotenv import load_dotenv

from src.fetcher import get_price_history, get_fundamentals
from src.processor import process_price_history, process_fundamentals
from src.analyst import analyse
from src.reporter import save_report

load_dotenv()


def run(ticker: str):
    print(f"Pobieram dane dla {ticker}...")
    raw_prices = get_price_history(ticker)
    raw_fundamentals = get_fundamentals(ticker)

    print("Przetwarzam dane...")
    prices = process_price_history(raw_prices)
    fundamentals = process_fundamentals(raw_fundamentals)

    print("Analizuję przez Gemini...")
    analysis = analyse(ticker, prices, fundamentals)

    filename = save_report(ticker, analysis)
    print(f"Gotowe! Raport zapisany: {filename}")


if __name__ == "__main__":
    ticker = input("Podaj ticker spółki (np. AAPL, CDR.WA): ").strip().upper()
    run(ticker)
