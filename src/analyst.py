import os
from google import genai

_client = None
# _client powstaje dopiero po pierwszym wywołaniu funkcji _get_client(), a nie przy starcie programu. Podkreślnik pokazuje, że jest to zmienna wewnętrzna.


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Brak GEMINI_API_KEY w zmiennych środowiskowych")
        _client = genai.Client(api_key=api_key)
    return _client


def analyse(ticker: str, prices: dict, fundamentals: dict) -> str:
    prompt = f"""
Jesteś analitykiem finansowym. Przeanalizuj poniższe dane i napisz zwięzły raport inwestycyjny po polsku.

Ticker: {ticker}

--- DANE RYNKOWE ({prices["period"]}) ---
Aktualna cena:     {prices["current_price"]}
Min / Max:         {prices["price_min"]} / {prices["price_max"]}
Zmiana w okresie:  {prices["price_change_pct"]}%

--- DANE FUNDAMENTALNE ---
Spółka:            {fundamentals["name"]}
Sektor:            {fundamentals["sector"]}
Branża:            {fundamentals["industry"]}
Kapitalizacja:     {fundamentals["market_cap"]}
P/E (trailing):    {fundamentals["pe_trailing"]}
P/E (forward):     {fundamentals["pe_forward"]}
P/BV:              {fundamentals["price_to_book"]}
Przychody:         {fundamentals["revenue"]}
Zysk netto:        {fundamentals["net_income"]}
Dług całkowity:    {fundamentals["total_debt"]}
ROE:               {fundamentals["roe"]}%
Stopa dywidendy:   {fundamentals["dividend_yield"]}%

Raport powinien zawierać:
1. Krótki opis spółki
2. Ocenę wyników i kondycji finansowej
3. Ocenę wyceny (czy drogo/tanio względem mnożników)
4. Główne ryzyka
5. Krótkie podsumowanie z rekomendacją (kup / trzymaj / sprzedaj)
"""
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text
