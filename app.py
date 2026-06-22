import base64
import io
from datetime import date

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageEnhance
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.analyst import analyse, compare
from src.fetcher import get_fundamentals, get_price_history, search_ticker, validate_ticker
from src.processor import process_fundamentals, process_price_history
from src.reporter import generate_pdf, list_reports, load_report, save_report

load_dotenv()


@st.cache_data(ttl=900)
def cached_price_history(ticker: str, period: str) -> dict:
    return get_price_history(ticker, period)


@st.cache_data(ttl=900)
def cached_fundamentals(ticker: str) -> dict:
    return get_fundamentals(ticker)


@st.cache_data(ttl=900)
def cached_validate_ticker(ticker: str) -> str | None:
    return validate_ticker(ticker)


def compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


@st.cache_data
def faded_image_to_base64(path: str, opacity: float = 0.15) -> str:
    img = Image.open(path).convert("L").convert("RGBA")
    img.putalpha(ImageEnhance.Brightness(img.split()[-1]).enhance(opacity))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


byk_b64 = faded_image_to_base64("assets/byk.webp")
dolar_b64 = faded_image_to_base64("assets/dolar.webp")


st.set_page_config(page_title="Analityk Finansowy Lucjuszek", page_icon="📈", layout="wide")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/png;base64,{byk_b64}), url(data:image/png;base64,{dolar_b64}), linear-gradient(180deg, #0b1f17 0%, #0e2a1c 100%);
        background-repeat: no-repeat, no-repeat, no-repeat;
        background-position: left bottom, right bottom, center;
        background-size: 45vw auto, 45vw auto, cover;
        background-attachment: fixed, fixed, fixed;
    }}
    [data-testid="stAppViewContainer"], [data-testid="stMain"], .main, .block-container {{
        background: transparent !important;
    }}
    h1, h2, h3, .stMarkdown p {{
        color: #f4d35e !important;
    }}
    div[data-testid="stMetric"] {{
        background: linear-gradient(135deg, #14532d, #1e7a3c);
        border: 1px solid #f4d35e;
        border-radius: 12px;
        padding: 12px;
    }}
    div[data-testid="stMetricLabel"] {{
        color: #f4d35e !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: #ffffff !important;
    }}
    .stButton button {{
        background-color: #f4d35e;
        color: #0b1f17;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }}
    .stButton button:hover {{
        background-color: #ffe8a3;
        color: #0b1f17;
    }}
    section[data-testid="stSidebar"] {{
        background-color: #0e2a1c;
    }}
    [data-testid="stStatusWidget"] svg {{
        display: none;
    }}
    [data-testid="stStatusWidget"]::before {{
        content: "$";
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        border: 3px solid #f4d35e;
        border-top-color: transparent;
        border-radius: 50%;
        font-weight: bold;
        font-size: 13px;
        color: #f4d35e;
        animation: dollar-spin 0.9s linear infinite;
    }}
    @keyframes dollar-spin {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 style='text-align: center;'>📈 Analityk Finansowy Lucjuszek</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #cfead9;'>Wpisz ticker spółki, wybierz okres i wygeneruj raport inwestycyjny.</p>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Historia raportów")
    saved_reports = list_reports()
    if not saved_reports:
        st.caption("Brak zapisanych raportów.")
    else:
        selected_report = st.selectbox("Wybierz raport", saved_reports)
        if st.button("Wyświetl"):
            st.session_state["viewed_report"] = load_report(selected_report)

if "viewed_report" in st.session_state:
    st.subheader("Podgląd zapisanego raportu")
    st.text(st.session_state["viewed_report"])
    st.divider()

with st.expander("🔍 Wyszukaj spółkę po nazwie"):
    company_name = st.text_input("Nazwa spółki", placeholder="np. Apple, Orlen, CD Projekt")
    if company_name:
        found = search_ticker(company_name)
        if not found:
            st.caption("Brak wyników.")
        for result in found[:5]:
            label = f"{result['symbol']} — {result['name']} ({result['exchange']})"
            if st.button(label, key=f"pick_{result['symbol']}"):
                st.session_state["ticker_input"] = result["symbol"]

col1, col2 = st.columns([2, 1])
with col1:
    ticker = st.text_input(
        "Ticker spółki",
        placeholder="np. AAPL, CDR.WA, PKN.WA",
        key="ticker_input",
    ).strip().upper()
with col2:
    period = st.selectbox("Okres analizy", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

ticker_valid = False
if ticker:
    company_found = cached_validate_ticker(ticker)
    if company_found:
        ticker_valid = True
        st.success(f"✅ Znaleziono: {company_found}")
    else:
        st.error(f"❌ Nie znaleziono spółki dla tickera „{ticker}”.")

run = st.button("Generuj raport", type="primary", disabled=not ticker_valid)

if run and ticker:
    st.session_state["active_ticker"] = ticker
    st.session_state["active_period"] = period
    st.session_state.pop("active_analysis", None)

if "active_ticker" in st.session_state:
    active_ticker = st.session_state["active_ticker"]
    active_period = st.session_state["active_period"]
    try:
        with st.spinner("Pobieram dane rynkowe..."):
            raw_prices = cached_price_history(active_ticker, active_period)
            raw_fundamentals = cached_fundamentals(active_ticker)

        prices = process_price_history(raw_prices)
        fundamentals = process_fundamentals(raw_fundamentals)

        st.subheader(f"{fundamentals['name']} ({active_ticker})")
        st.caption(f"{fundamentals['sector']} · {fundamentals['industry']}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Aktualna cena", f"{prices['current_price']}")
        m2.metric(
            "Zmiana w okresie",
            f"{prices['price_change_pct']}%",
            delta=f"{prices['price_change_pct']}%",
        )
        m3.metric("Min / Max", f"{prices['price_min']} / {prices['price_max']}")
        m4.metric("Kapitalizacja", fundamentals["market_cap"] or "—")

        st.divider()

        tab_chart, tab_fundamentals, tab_report = st.tabs(
            ["📊 Wykres", "📋 Dane fundamentalne", "🧠 Raport AI"]
        )

        with tab_chart:
            close = pd.Series(
                list(raw_prices["prices"].values()),
                index=pd.to_datetime(list(raw_prices["prices"].keys())),
                name="Cena zamknięcia",
            )

            indicator_choices = st.multiselect(
                "Wskaźniki techniczne",
                ["SMA 20", "SMA 50", "SMA 200", "EMA 20", "EMA 50", "Bollinger Bands", "RSI (14)"],
                default=["SMA 20", "SMA 50"],
            )

            show_rsi = "RSI (14)" in indicator_choices
            rows = 2 if show_rsi else 1
            fig = make_subplots(
                rows=rows,
                cols=1,
                shared_xaxes=True,
                row_heights=[0.7, 0.3] if show_rsi else [1],
                vertical_spacing=0.05,
            )

            fig.add_trace(
                go.Scatter(x=close.index, y=close, name="Cena zamknięcia", line=dict(color="#f4d35e", width=2)),
                row=1, col=1,
            )

            sma_windows = {"SMA 20": 20, "SMA 50": 50, "SMA 200": 200}
            ema_windows = {"EMA 20": 20, "EMA 50": 50}

            for label, window in sma_windows.items():
                if label in indicator_choices:
                    if len(close) >= window:
                        sma = close.rolling(window).mean()
                        fig.add_trace(go.Scatter(x=sma.index, y=sma, name=label), row=1, col=1)
                    else:
                        st.caption(f"Za mało danych dla {label} (potrzeba {window} dni, jest {len(close)}).")

            for label, window in ema_windows.items():
                if label in indicator_choices:
                    if len(close) >= window:
                        ema = close.ewm(span=window, adjust=False).mean()
                        fig.add_trace(go.Scatter(x=ema.index, y=ema, name=label), row=1, col=1)
                    else:
                        st.caption(f"Za mało danych dla {label} (potrzeba {window} dni, jest {len(close)}).")

            if "Bollinger Bands" in indicator_choices:
                if len(close) >= 20:
                    mid = close.rolling(20).mean()
                    std = close.rolling(20).std()
                    upper, lower = mid + 2 * std, mid - 2 * std
                    fig.add_trace(go.Scatter(x=upper.index, y=upper, name="Bollinger górne", line=dict(color="gray", dash="dot")), row=1, col=1)
                    fig.add_trace(go.Scatter(x=lower.index, y=lower, name="Bollinger dolne", line=dict(color="gray", dash="dot")), row=1, col=1)
                else:
                    st.caption(f"Za mało danych dla Bollinger Bands (potrzeba 20 dni, jest {len(close)}).")

            if show_rsi:
                rsi = compute_rsi(close)
                fig.add_trace(go.Scatter(x=rsi.index, y=rsi, name="RSI (14)", line=dict(color="#1e7a3c")), row=2, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)

            fig.update_layout(
                height=550 if show_rsi else 450,
                margin=dict(l=10, r=10, t=30, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                hovermode="x unified",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(14,42,28,0.4)",
                font=dict(color="#f4d35e"),
            )
            fig.update_xaxes(
                rangeslider_visible=not show_rsi,
                rangeselector=dict(
                    buttons=[
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=3, label="3m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="1r", step="year", stepmode="backward"),
                        dict(step="all", label="Cały okres"),
                    ]
                ),
                row=1, col=1,
            )

            st.plotly_chart(fig, use_container_width=True)

        with tab_fundamentals:
            table = {
                "P/E (trailing)": fundamentals["pe_trailing"],
                "P/E (forward)": fundamentals["pe_forward"],
                "P/BV": fundamentals["price_to_book"],
                "Przychody": fundamentals["revenue"],
                "Zysk netto": fundamentals["net_income"],
                "Dług": fundamentals["total_debt"],
                "ROE": f"{fundamentals['roe']}%" if fundamentals["roe"] else "—",
                "Dywidenda": f"{fundamentals['dividend_yield']}%" if fundamentals["dividend_yield"] else "—",
            }
            st.table(pd.DataFrame(table.items(), columns=["Wskaźnik", "Wartość"]))

        with tab_report:
            if "active_analysis" not in st.session_state:
                with st.spinner("Analizuję spółkę specjalnie dla Ciebie mistrzu..."):
                    st.session_state["active_analysis"] = analyse(active_ticker, prices, fundamentals)

            analysis = st.session_state["active_analysis"]
            st.markdown(analysis)

            filename = save_report(active_ticker, analysis)
            pdf_bytes = generate_pdf(active_ticker, analysis)

            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                with open(filename, "rb") as f:
                    st.download_button(
                        label="Pobierz raport (.txt)",
                        data=f,
                        file_name=filename,
                        mime="text/plain",
                    )
            with dl_col2:
                st.download_button(
                    label="Pobierz raport (.pdf)",
                    data=pdf_bytes,
                    file_name=f"raport_{active_ticker}_{date.today()}.pdf",
                    mime="application/pdf",
                )

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Nieoczekiwany błąd: {e}")

st.divider()
st.header("🆚 Porównanie spółek")

compare_input = st.text_input(
    "Tickery do porównania (oddzielone przecinkami)",
    placeholder="np. AAPL, MSFT, NVDA",
)
compare_run = st.button("Porównaj", disabled=not compare_input)

if compare_run and compare_input:
    tickers_list = [t.strip().upper() for t in compare_input.split(",") if t.strip()]

    if len(tickers_list) < 2:
        st.warning("Podaj co najmniej dwa tickery.")
    else:
        try:
            companies = []
            comparison_rows = {}

            with st.spinner("Pobieram dane spółek..."):
                for t in tickers_list:
                    p = process_price_history(cached_price_history(t, period))
                    f = process_fundamentals(cached_fundamentals(t))
                    companies.append({"ticker": t, "prices": p, "fundamentals": f})
                    comparison_rows[t] = {
                        "Cena": p["current_price"],
                        "Zmiana": f"{p['price_change_pct']}%",
                        "P/E": f["pe_trailing"],
                        "P/BV": f["price_to_book"],
                        "ROE": f"{f['roe']}%" if f["roe"] else "—",
                        "Dywidenda": f"{f['dividend_yield']}%" if f["dividend_yield"] else "—",
                        "Kapitalizacja": f["market_cap"] or "—",
                    }

            st.subheader("Tabela porównawcza")
            st.table(pd.DataFrame(comparison_rows))

            with st.spinner("Analizuję porównanie przez Gemini..."):
                comparison_text = compare(companies)

            st.subheader("Analiza porównawcza AI")
            st.markdown(comparison_text)

        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Nieoczekiwany błąd: {e}")
