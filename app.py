import yfinance as yf
import pandas as pd
import numpy as np
import requests
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()

def calculate_beta_1yr(stock_symbol, market_symbol="^NSEI"):
    # Stock prices for past 1 year
    stock_data = yf.download(stock_symbol, period="12mo")['Close']
    market_data = yf.download(market_symbol, period="12mo")['Close']
    
    # Daily returns
    stock_returns = stock_data.pct_change().dropna()
    market_returns = market_data.pct_change().dropna()

    # Align lengths
    min_len = min(len(stock_returns), len(market_returns))
    stock_returns = stock_returns[-min_len:]
    market_returns = market_returns[-min_len:]

    print(stock_returns)
    # Covariance / Variance
    cov_matrix = np.cov(stock_returns, market_returns)
    beta = cov_matrix[0,1] / cov_matrix[1,1]

    return round(beta, 2)

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    # --- MACD ---
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    def macd_indicator(row):
        if row['MACD'] > row['Signal']:
            if row['MACD'] > 0 and row['Signal'] > 0:
                return "Strong Buy"
            return "Buy"
        elif row['MACD'] < row['Signal']:
            if row['MACD'] < 0 and row['Signal'] < 0:
                return "Strong Sell"
            return "Sell"
        else:
            return "Neutral"

    df['MACD_Indicator'] = df.apply(macd_indicator, axis=1)
    def rsi_indicator(value):
        if pd.isna(value):
            return "Neutral"
        if value < 30:
            return "Strong Sell"
        elif 30 <= value < 40:
            return "Sell"
        elif 40 <= value < 60:
            return "Buy"
        elif 60 <= value < 70:
            return "Strong Buy"
        else: 
            return "Sell(Apply stop loss)"
    # --- RSI ---
    delta = df['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    # Use Wilder’s smoothing (EMA with alpha=1/14)
    avg_gain = pd.Series(gain).ewm(alpha=1/14, adjust=False).mean()
    avg_loss = pd.Series(loss).ewm(alpha=1/14, adjust=False).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['RSI_Indicator'] = df['RSI'].apply(rsi_indicator)
    
    # --- ADX ---
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L','H-PC','L-PC']].max(axis=1)

    df['+DM'] = np.where((df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']),
                         df['High'] - df['High'].shift(1), 0)
    df['+DM'] = np.where(df['+DM'] < 0, 0, df['+DM'])

    df['-DM'] = np.where((df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)),
                         df['Low'].shift(1) - df['Low'], 0)
    df['-DM'] = np.where(df['-DM'] < 0, 0, df['-DM'])

    tr14 = df['TR'].ewm(alpha=1/14, adjust=False).mean()
    plus_dm14 = df['+DM'].ewm(alpha=1/14, adjust=False).mean()
    minus_dm14 = df['-DM'].ewm(alpha=1/14, adjust=False).mean()

    plus_di14 = 100 * (plus_dm14 / tr14)
    minus_di14 = 100 * (minus_dm14 / tr14)

    dx = (abs(plus_di14 - minus_di14) / (plus_di14 + minus_di14)) * 100
    
    def adx_indicator(value):
        if pd.isna(value):
            return "Neutral"
        if value < 20:
            return "Sell"
        elif 20<= value < 25:
            return "Buy in small quantity"
        elif 25 <= value < 40:
            return "Buy"
        elif 40<= value < 50: 
            return "Strong Buy"
        else:
            return "Very Strong Trend(Exercise caution)"
        
    df['ADX'] = dx.ewm(alpha=1/14, adjust=False).mean()
    df['ADX_Indicator'] = df['ADX'].apply(adx_indicator)
    # --- Moving Averages (MA7, MA13) ---
    df['MA7'] = df['Close'].rolling(window=7).mean()
    df['MA13'] = df['Close'].rolling(window=13).mean()

    def ma_indicator(row):
        if pd.isna(row['MA7']) or pd.isna(row['MA13']):
            return "Neutral"
        diff = row['MA7'] - row['MA13']
        if diff > 0:
            if 0 < diff <= 1:   # very close, stronger signal
                return "7 Crossed above 13"
            return "Buy"
        elif diff < 0:
            if -1 <= diff < 0:  # very close, stronger signal
                return "7 Crossed below 13"
            return "Sell"
        else:
            return "Neutral"

    df['MA_Indicator'] = df.apply(ma_indicator, axis=1)

    # cleanup temp cols
    df = df[[
        'Date','Open','High','Low','Close','Volume',
        'MACD','Signal','MACD_Indicator','MA7','MA13',
        'MA_Indicator','RSI','RSI_Indicator','ADX','ADX_Indicator']]

    return df
# Setup templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def lookup_symbol(query: str, region: str = "IN", lang: str = "en-IN", limit: int = 10, exchange: str = "NSE"):
    """
    Lookup stock symbols using Yahoo Finance's search endpoint.
    Filters for NSE by default.
    """
    url = "https://query1.finance.yahoo.com/v1/finance/search"
    params = {
        "q": query,
        "quotesCount": limit,
        "newsCount": 0,
        "lang": lang,
        "region": region
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/123.0.0.0 Safari/537.36"
    }
    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()

    results = []
    for item in data.get("quotes", []):
        if not item.get("symbol"):
            continue
        if exchange and item.get("exchDisp") and item["exchDisp"].upper() != exchange.upper():
            continue
        results.append({
            "symbol": item.get("symbol"),
            "shortname": item.get("shortname") or item.get("longname"),
            "longname": item.get("longname") or item.get("shortname"),
            "exchange": item.get("exchDisp"),
            "type": item.get("quoteType"),
        })

    return results


@app.get("/", response_class=HTMLResponse)
async def search_form(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
async def search_company(request: Request, company_name: str = Form(...)):
    results = lookup_symbol(company_name, exchange="NSE")
    return templates.TemplateResponse("results.html", {"request": request, "results": results, "company_name": company_name})


@app.post("/history", response_class=HTMLResponse)
async def get_history(request: Request, symbol: str = Form(...)):
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    df = yf.download(symbol, period="12mo", interval="1d")
    if df.empty:
        return templates.TemplateResponse(
            "history.html",
            {"request": request, "symbol": symbol, "data": [], "error": "No data found"}
        )

    df = df.reset_index()

    # Flatten columns if multi-index
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    df = calculate_indicators(df)

    data = df.round(2).tail(7).to_dict(orient="records")
    
    # Calculate 1-year beta
    beta = calculate_beta_1yr(symbol)
    print(beta)
    return templates.TemplateResponse(
        "history.html",
        {"request": request, "symbol": symbol, "data": data, "beta":beta}
    )


if __name__ == "__main__":
    #MACD RSI ADX
    uvicorn.run(app, host="0.0.0.0", port=8000)
