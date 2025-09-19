# main.py
import yfinance as yf
import pandas as pd
import uvicorn
import json
from datetime import datetime

from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware

from finance.beta import calculate_beta_1yr
from finance.from_yfinance import get_info_from_yfinance, lookup_symbol
from finance.roce import get_roce
from finance.indicators import calculate_indicators
from finance.utils import *

app = FastAPI()

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/search")
async def search_company(company_name: str = Form(...)):
    results = lookup_symbol(company_name, exchange="NSE")
    return {"results": results, "company_name": company_name}


@app.post("/history")
async def get_history(symbol: str = Form(...)):
    if not symbol.endswith(".NS"):
        symbol += ".NS"

    df = yf.download(symbol, period="12mo", interval="1d")
    if df.empty:
        return {"symbol": symbol, "data": None, "beta": None, "error": "No data found"}

    df = df.reset_index()
    df = calculate_indicators(df)

    # Clean column names (remove tuples)
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

    # Convert last row to JSON-friendly dict
    last_row = json.loads(df.round(2).tail(1).to_json(orient="records"))[0]
    last_row["Date"] = datetime.fromtimestamp(last_row["Date"] / 1000).strftime("%Y-%m-%d")

    technical = []
    for k, v in last_row.items():
        if k in ["MA7", "MA13", "MACD", "Signal", "MA100", "MA200"]:
            continue  # skip here, handled later
        if k == "Date":
            technical.append({"key": "Date", "value": [v, "gray", "Neutral"]})
        else:
            color, label = get_color(k, v)
            technical.append({"key": k, "value": [v, color, label]})

    # --- MA13/MA7 ---
    ma13 = last_row["MA13"]
    ma7 = last_row["MA7"]
    close = last_row.get("Close")
    if close is not None and ma7 is not None and ma13 is not None:
        color, label = get_ma_color(ma13, ma7)
        technical.append({"key": "Price/MA7/MA13", "value": [f"{close}/{ma7}/{ma13}", color, label]})
    technical.append({"key": "MA13/MA7", "value": [f"{close}/{ma7}/{ma13}", color, label]})

    # --- MA100/MA200 ---
    ma100 = last_row.get("MA100")
    ma200 = last_row.get("MA200")
    close = last_row.get("Close")
    if close is not None and ma100 is not None and ma200 is not None:
        color, label = get_price_vs_ma100_200_color(close, ma100, ma200)
        technical.append({"key": "Price/MA100/MA200", "value": [f"{close}/{ma100}/{ma200}", color, label]})

    # --- MACD/Signal ---
    macd = last_row["MACD"]
    signal = last_row["Signal"]
    technical.append(build_macd_signal_key(macd, signal))

    print(last_row)

    beta = calculate_beta_1yr(symbol)
    info = get_info_from_yfinance(symbol)
    roce = get_roce(symbol)

    fundemental = {
        "beta": round(beta, 2) if beta else None,
        "PE": round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else None,
        "EPS": round(info.get("trailingEps", 0), 2) if info.get("trailingEps") else None,
        "LTP": round(info.get("currentPrice", 0), 2) if info.get("currentPrice") else None,
        "MarketCap": f"{int(int(info.get('marketCap', 0)) / 10000000):,}",
        "bookValue": round(info.get("bookValue", 0), 2) if info.get("bookValue") else None,
        "debtToEquity": round(info.get("debtToEquity", 0), 2) if info.get("debtToEquity") else None,
        "priceToBook": round(info.get("priceToBook", 0), 2) if info.get("priceToBook") else None,
        "roce": round(roce, 2) if roce else None,
    }

    return {"symbol": symbol, "data": technical, "result": fundemental}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
