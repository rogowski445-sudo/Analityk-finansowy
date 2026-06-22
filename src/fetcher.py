import yfinance as yf

# yf to skrót od Yahoo Finance, biblioteka umożliwiająca pobieranie danych finansowych z Yahoo Finance.


def get_price_history(ticker: str, period: str = "1y") -> dict:
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    if hist.empty:
        raise ValueError(f"Brak danych dla tickera: {ticker}")
    return {
        "ticker": ticker,
        "period": period,
        "prices": hist["Close"].round(2).to_dict(),
    }


def get_fundamentals(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    info = stock.info
    keys = [
        "shortName", "sector", "industry",
        "marketCap", "trailingPE", "forwardPE",
        "priceToBook", "totalRevenue", "netIncomeToCommon",
        "totalDebt", "returnOnEquity", "dividendYield",
    ]
    return {k: info.get(k) for k in keys}


def search_ticker(query: str) -> list[dict]:
    results = yf.Search(query).quotes
    return [
        {"symbol": r.get("symbol"), "name": r.get("longname") or r.get("shortname"), "exchange": r.get("exchDisp")}
        for r in results
        if r.get("quoteType") == "EQUITY"
    ]


def validate_ticker(ticker: str) -> str | None:
    info = yf.Ticker(ticker).info
    return info.get("shortName") or info.get("longName")
