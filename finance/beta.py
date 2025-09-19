import yfinance as yf
import pandas as pd
import numpy as np

def calculate_beta_1yr(stock_symbol, market_symbol="^NSEI"):
    # Download data
    data = yf.download([stock_symbol, market_symbol], period="12mo")['Close'].dropna()

    if stock_symbol not in data or market_symbol not in data:
        return None

    # Daily returns aligned by date
    returns = data.pct_change().dropna()
    stock_ret = returns[stock_symbol]
    market_ret = returns[market_symbol]

    if len(stock_ret) < 2:
        return None

    # Beta = Cov(stock, market) / Var(market)
    cov_matrix = np.cov(stock_ret, market_ret, ddof=1)
    beta = cov_matrix[0, 1] / cov_matrix[1, 1]

    return round(beta, 2)
