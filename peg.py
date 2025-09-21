
import yfinance as yf

ticker = yf.Ticker("ADANIENT.NS")
info = ticker.info

for key in info:
    if "gross" in key.lower():
        print(f"{key}: {info[key]}")