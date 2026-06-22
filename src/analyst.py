import os
import time
from datetime import date

from google import genai
from google.genai.errors import ServerError

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


def _generate(prompt: str) -> str:
    client = _get_client()
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text
        except ServerError:
            if attempt == max_attempts:
                raise
            time.sleep(attempt * 5)


def analyse(ticker: str, prices: dict, fundamentals: dict) -> str:
    prompt = f"""
Jesteś analitykiem finansowym. Przeanalizuj poniższe dane i napisz zwięzły raport inwestycyjny po polsku.
Dzisiejsza data to {date.today().strftime('%d.%m.%Y')}. Nie dodawaj własnego nagłówka, tytułu ani daty na początku odpowiedzi — zacznij od razu od treści analizy.

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
    return _generate(prompt)


def compare(companies: list[dict]) -> str:
    blocks = []
    for c in companies:
        prices, fundamentals = c["prices"], c["fundamentals"]
        blocks.append(f"""
Ticker: {c["ticker"]}
Spółka:            {fundamentals["name"]}
Sektor:            {fundamentals["sector"]}
Aktualna cena:     {prices["current_price"]}
Zmiana w okresie:  {prices["price_change_pct"]}%
Kapitalizacja:     {fundamentals["market_cap"]}
P/E (trailing):    {fundamentals["pe_trailing"]}
P/BV:              {fundamentals["price_to_book"]}
ROE:               {fundamentals["roe"]}%
Dług całkowity:    {fundamentals["total_debt"]}
Stopa dywidendy:   {fundamentals["dividend_yield"]}%
""")

    prompt = f"""
Jesteś analitykiem finansowym. Porównaj poniższe spółki i napisz zwięzłą analizę porównawczą po polsku.
Dzisiejsza data to {date.today().strftime('%d.%m.%Y')}. Nie dodawaj własnego nagłówka, tytułu ani daty na początku odpowiedzi — zacznij od razu od treści analizy.

{"".join(blocks)}

Analiza powinna zawierać:
1. Która spółka wygląda najatrakcyjniej pod względem wyceny i dlaczego
2. Która ma najlepszą kondycję finansową (rentowność, dług)
3. Główne różnice między spółkami
4. Krótkie podsumowanie — które miejsce w rankingu zajmuje każda spółka i dlaczego
"""
    return _generate(prompt)
