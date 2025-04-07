import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="Intrinsic Value Screener", layout="wide")

stocks = [
    "TCS", "INFY", "RELIANCE", "HDFCBANK", "ITC", "LT", "KOTAKBANK",
    "AXISBANK", "SBIN", "WIPRO"
]

def get_market_price(symbol):
    url = f"https://www.google.com/finance/quote/{symbol}:NSE"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.find("div", class_="YMlKec fxKbKc")
        if price_tag:
            return float(price_tag.text.replace('₹', '').replace(',', ''))
    except:
        return None

def get_financials_screener(symbol):
    url = f"https://www.screener.in/company/{symbol}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        eps_tag = soup.find("li", string=lambda s: s and "EPS" in s)
        book_value_tag = soup.find("li", string=lambda s: s and "Book value" in s)
        roe_tag = soup.find("li", string=lambda s: s and "ROE" in s)

        eps = float(eps_tag.text.split(':')[-1].strip()) if eps_tag else 0
        growth = float(roe_tag.text.split(':')[-1].replace('%', '').strip()) if roe_tag else 10

        return eps, growth
    except:
        return 0, 10

def calculate_intrinsic_value(eps, growth):
    return round(eps * (8.5 + 2 * growth), 2)

st.title("📊 Indian Stock Intrinsic Value Dashboard")

results = []

for symbol in stocks:
    with st.spinner(f"Processing {symbol}..."):
        eps, growth = get_financials_screener(symbol)
        intrinsic_value = calculate_intrinsic_value(eps, growth)
        market_price = get_market_price(symbol)

        if eps == 0 or market_price is None:
            continue

        undervalued = intrinsic_value > market_price

        results.append({
            "Stock": symbol,
            "EPS": eps,
            "Growth %": growth,
            "Intrinsic Value": intrinsic_value,
            "Market Price": market_price,
            "Undervalued": "✅ Yes" if undervalued else "❌ No"
        })
        time.sleep(1)

if results:
    df = pd.DataFrame(results)
    df = df.sort_values(by="Undervalued", ascending=False)
    st.dataframe(df, use_container_width=True)
else:
    st.error("No data available. Try again later or check API limits.")
