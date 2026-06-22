# Financial Research Agent

Agent do automatycznej analizy finansowej spółek giełdowych. Pobiera dane rynkowe i fundamentalne, a następnie generuje raport inwestycyjny przy pomocy modelu Gemini 2.5 Flash.

Projekt stworzony przeze mnie przy pomocy Claude Code

## Architektura

```
yfinance → processor → Gemini 2.5 Flash → raport .txt
```

| Moduł | Rola |
|---|---|
| `src/fetcher.py` | Pobieranie danych z Yahoo Finance (kursy + fundamenty) |
| `src/processor.py` | Czyszczenie i formatowanie danych |
| `src/analyst.py` | Analiza przez Gemini API |
| `src/reporter.py` | Zapis raportu do pliku `.txt` |
| `main.py` | Punkt wejścia — spina wszystkie moduły |

## Wymagania

- Python 3.10+
- Klucz API Google Gemini ([console.cloud.google.com](https://console.cloud.google.com))

## Instalacja

```bash
git clone https://github.com/twój-username/financial-agent.git
cd financial-agent
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

```bash
python main.py
```

Program zapyta o ticker spółki:

```
Podaj ticker spółki (np. AAPL, CDR.WA): AAPL
Pobieram dane dla AAPL...
Przetwarzam dane...
Analizuję przez Gemini...
Gotowe! Raport zapisany: raport_AAPL_2026-06-16.txt
```

Raport pojawi się w folderze projektu jako plik `.txt`.

## Obsługiwane rynki

- **USA** — np. `AAPL`, `MSFT`, `NVDA`
- **GPW (Polska)** — np. `CDR.WA`, `PKN.WA`, `LPP.WA`
- Każda spółka dostępna w Yahoo Finance

