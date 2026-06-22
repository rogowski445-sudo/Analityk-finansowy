# Financial Research Agent - Lucjuszek

Agent do automatycznej analizy finansowej spółek giełdowych. Pobiera dane rynkowe i fundamentalne, a następnie generuje raport inwestycyjny przy pomocy modelu Gemini 2.5 Flash. Dostępny jako interaktywna aplikacja webowa (Streamlit) oraz wersja konsolowa.

Projekt stworzony przy pomocy Claude Code (Anthropic)

## Architektura

```
yfinance → processor → Gemini 2.5 Flash → raport (.txt / .pdf)
```

| Moduł | Rola |
|---|---|
| `src/fetcher.py` | Pobieranie danych z Yahoo Finance (kursy, fundamenty, wyszukiwanie, walidacja tickera) |
| `src/processor.py` | Czyszczenie i formatowanie danych |
| `src/analyst.py` | Analiza i porównanie spółek przez Gemini API |
| `src/reporter.py` | Zapis raportu do `.txt` i `.pdf`, historia raportów |
| `app.py` | Aplikacja webowa Streamlit — główny interfejs |
| `main.py` | Wersja konsolowa |

## Funkcje

- Pojedyncza analiza spółki z wykresem (SMA, EMA, Bollinger Bands, RSI)
- Porównanie kilku spółek naraz z jedną zbiorczą analizą AI
- Wyszukiwanie tickera po nazwie spółki + walidacja w czasie rzeczywistym
- Eksport raportu do `.txt` i `.pdf`
- Historia wcześniej wygenerowanych raportów
- Testy jednostkowe (`pytest`) dla logiki przetwarzania danych

## Wymagania

- Python 3.10+
- Klucz API Google Gemini ([aistudio.google.com](https://aistudio.google.com))

## Instalacja

```bash
git clone https://github.com/rogowski445-sudo/Financial-Analyst-Lucjuszek.git
cd Financial-Analyst-Lucjuszek
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
```

Skopiuj `.env.example` do `.env` i wpisz klucz:

```bash
cp .env.example .env
```

```
GEMINI_API_KEY=twój_klucz_tutaj
```

## Użycie

**Aplikacja webowa (zalecane):**

```bash
streamlit run app.py
```

Albo dwuklik na `start.bat` (Windows).

**Wersja konsolowa:**

```bash
python main.py
```

```
Podaj ticker spółki (np. AAPL, CDR.WA): AAPL
Pobieram dane dla AAPL...
Przetwarzam dane...
Analizuję przez Gemini...
Gotowe! Raport zapisany: reports/raport_AAPL_2026-06-16.txt
```

## Testy

```bash
python -m pytest tests/ -v
```

## Obsługiwane rynki

- **USA** — np. `AAPL`, `MSFT`, `NVDA`
- **GPW (Polska)** — np. `CDR.WA`, `PKN.WA`, `LPP.WA`
- Każda spółka dostępna w Yahoo Finance
