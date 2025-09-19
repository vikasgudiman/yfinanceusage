
import yfinance as yf

ticker = yf.Ticker("RELIANCE.NS")
info = ticker.info

for key in info:
    print(f"{key}: {info[key]}")