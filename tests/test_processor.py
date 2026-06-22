from src.processor import process_fundamentals, process_price_history


def test_process_price_history_basic_stats():
    raw = {
        "ticker": "AAPL",
        "period": "1y",
        "prices": {
            "2025-01-01": 100.0,
            "2025-06-01": 80.0,
            "2025-12-01": 120.0,
        },
    }
    result = process_price_history(raw)
    assert result["ticker"] == "AAPL"
    assert result["period"] == "1y"
    assert result["current_price"] == 120.0
    assert result["price_min"] == 80.0
    assert result["price_max"] == 120.0
    assert result["price_change_pct"] == 20.0


def test_process_price_history_negative_change():
    raw = {
        "ticker": "XYZ",
        "period": "6mo",
        "prices": {"d1": 200.0, "d2": 150.0},
    }
    result = process_price_history(raw)
    assert result["price_change_pct"] == -25.0


def test_process_fundamentals_formats_large_numbers():
    raw = {
        "shortName": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "marketCap": 2_500_000_000_000,
        "trailingPE": 28.5,
        "forwardPE": 26.1,
        "priceToBook": 45.2,
        "totalRevenue": 390_000_000_000,
        "netIncomeToCommon": 95_000_000,
        "totalDebt": 120_000_000_000,
        "returnOnEquity": 1.5,
        "dividendYield": 0.58,
    }
    result = process_fundamentals(raw)
    assert result["name"] == "Apple Inc."
    assert result["market_cap"] == "2500.00B"
    assert result["revenue"] == "390.00B"
    assert result["net_income"] == "95.00M"
    assert result["roe"] == 150.0
    assert result["dividend_yield"] == 0.58


def test_process_fundamentals_handles_missing_values():
    raw = {"shortName": "No Dividend Inc."}
    result = process_fundamentals(raw)
    assert result["dividend_yield"] is None
    assert result["roe"] is None
    assert result["market_cap"] is None
