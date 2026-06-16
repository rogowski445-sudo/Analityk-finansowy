def process_price_history(raw: dict) -> dict:
    prices = list(raw["prices"].values())
    return {
        "ticker": raw["ticker"],
        "period": raw["period"],
        "current_price": prices[-1],
        "price_min": round(min(prices), 2),
        "price_max": round(max(prices), 2),
        "price_change_pct": round(
            (prices[-1] - prices[0]) / prices[0] * 100,
            2,
        ),
    }

# raw - zmienna dla surowych danych, które są przetwarzane przez funkcję process_fundamentals.


def process_fundamentals(raw: dict) -> dict:
    def fmt_pomocnicza(val):
        if val is None:
            return None
        if val >= 1_000_000_000:
            return f"{val / 1_000_000_000:.2f}B"
        if val >= 1_000_000:
            return f"{val / 1_000_000:.2f}M"
        return val

    return {
        "name": raw.get("shortName"),
        "sector": raw.get("sector"),
        "industry": raw.get("industry"),
        "market_cap": fmt_pomocnicza(raw.get("marketCap")),
        "pe_trailing": raw.get("trailingPE"),
        "pe_forward": raw.get("forwardPE"),
        "price_to_book": raw.get("priceToBook"),
        "revenue": fmt_pomocnicza(raw.get("totalRevenue")),
        "net_income": fmt_pomocnicza(raw.get("netIncomeToCommon")),
        "total_debt": fmt_pomocnicza(raw.get("totalDebt")),
        "roe": round(raw.get("returnOnEquity") * 100, 2) if raw.get("returnOnEquity") else None,
        "dividend_yield": round(raw.get("dividendYield") * 100, 2) if raw.get("dividendYield") else None,
    }
