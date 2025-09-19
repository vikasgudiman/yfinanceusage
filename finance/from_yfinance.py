import yfinance as yf
import requests

def get_info_from_yfinance(stock_symbol):
    ticker = yf.Ticker(stock_symbol)
    info = ticker.info

    return info

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