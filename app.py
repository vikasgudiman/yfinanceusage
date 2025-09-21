# main.py
import yfinance as yf
import pandas as pd
import uvicorn
import json
import os
from datetime import datetime

from fastapi import FastAPI, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from finance.beta import calculate_beta_1yr
from finance.from_yfinance import get_info_from_yfinance, lookup_symbol
from finance.roce import get_roce
from finance.indicators import calculate_indicators
from finance.utils import *
from finance.excel_reader import read_data

app = FastAPI()

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FileRequest(BaseModel):
    file_path: str

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

    beta = calculate_beta_1yr(symbol)
    info = get_info_from_yfinance(symbol)
    roce = get_roce(symbol)

    fundamental = {
    # Existing keys
    "beta": round(beta, 2) if beta else None,
    "PE": round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else None,
    "EPS": round(info.get("trailingEps", 0), 2) if info.get("trailingEps") else None,
    "LTP": round(info.get("currentPrice", 0), 2) if info.get("currentPrice") else None,
    "bookValue": round(info.get("bookValue", 0), 2) if info.get("bookValue") else None,
    "debtToEquity": round(info.get("debtToEquity", 0), 2) if info.get("debtToEquity") else None,
    "priceToBook": round(info.get("priceToBook", 0), 2) if info.get("priceToBook") else None,
    "roce": round(roce, 2) if roce else None,

    # Converted to crore
    "MarketCap (in cr)": round(info.get("marketCap", 0) / 1e7, 2) if info.get("marketCap") else None,
    "Revenue (in cr)": round(info.get("totalRevenue", 0) / 1e7, 2) if info.get("totalRevenue") else None,
    "GrossProfit (in cr)": round(info.get("grossProfits", 0) / 1e7, 2) if info.get("grossProfits") else None,
    "NetProfit (in cr)": round(info.get("netIncomeToCommon", 0) / 1e7, 2) if info.get("netIncomeToCommon") else None,
    "Equity (in cr)": round((info.get("bookValue", 0) * info.get("sharesOutstanding", 0)) / 1e7, 2) if info.get("bookValue") and info.get("sharesOutstanding") else None,

    # Other added keys
    "RevenueGrowth%": round(info.get("revenueGrowth", 0) * 100, 2) if info.get("revenueGrowth") else None,
    "EarningsGrowth%": round(info.get("earningsGrowth", 0) * 100, 2) if info.get("earningsGrowth") else None,
    "EPSForward": round(info.get("epsForward", 0), 2) if info.get("epsForward") else None,
    "EPS%Increase": round(((info.get("epsForward", 0) - info.get("trailingEps", 0)) / info.get("trailingEps", 1)) * 100, 2) if info.get("trailingEps") else None,
    "ROE%": round((info.get("netIncomeToCommon", 0) / (info.get("bookValue", 0) * info.get("sharesOutstanding", 1))) * 100, 2) if info.get("bookValue") and info.get("sharesOutstanding") else None,
    }
    return {"symbol": symbol, "data": technical, "result": fundamental}

@app.post("/get-stocks/")
def get_stocks(request: FileRequest):
    file_path = request.file_path

    try:
        # Optional: check if file exists
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        stock_names = read_data(file_path)
        
        return {"stock_names": stock_names}
    except Exception as e:
        return {"error": str(e)}
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
