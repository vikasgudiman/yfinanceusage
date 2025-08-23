
import yfinance as yf

ticker = yf.Ticker("RELIANCE.NS")
info = ticker.info

for key in info:
    if "beta" in key.lower():
        print(f"{key}: {info[key]}")