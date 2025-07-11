import yfinance as yf

data = yf.download("EURUSD=X", start="2023-01-01", end="2023-12-31", interval="3mo")
data.to_csv("data/EURUSD.csv")
import streamlit as st

st.set_page_config(page_title="AlphaForgeFX", layout="wide")

st.title("📈 AlphaForgeFX — Quant FX Strategy Lab")

st.markdown("Welcome to the AlphaForgeFX Quant Strategy Builder & Backtester.")

st.sidebar.header("Strategy Options")
st.sidebar.text("Configure your model rules here.")
