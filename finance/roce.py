import yfinance as yf

def get_roce(ticker_symbol: str):
    try:
        ticker = yf.Ticker(ticker_symbol)
        ebit = ticker.financials.loc["Operating Income"].iloc[0]
        total_assets = ticker.balance_sheet.loc["Total Assets"].iloc[0]
        current_liabilities = ticker.balance_sheet.loc["Current Liabilities"].iloc[0]

        capital_employed = total_assets - current_liabilities
        roce = (ebit / capital_employed) * 100
        return round(roce, 2)

    except Exception as e:
        print(f"Could not calculate ROCE for {ticker_symbol}: {e}")
        return None
