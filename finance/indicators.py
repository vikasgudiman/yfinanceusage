import pandas as pd
import numpy as np

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate MACD, RSI, ADX, and Moving Averages with indicators.
    Returns the DataFrame with indicator columns appended.
    """

    # ---------------- MACD ----------------
    def add_macd(df: pd.DataFrame) -> pd.DataFrame:
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

        return df

    # ---------------- RSI ----------------
    def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        # Ensure Close is 1D
        close = df['Close'].squeeze()

        # Compute gains and losses
        delta = close.diff()
        gain = delta.copy()
        gain[delta < 0] = 0
        loss = delta.copy()
        loss[delta > 0] = 0
        loss = -loss  # make losses positive

        # Average gains and losses
        avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

        # RSI calculation
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Vectorized RSI indicator
        return df


    # ---------------- ADX ----------------
    def add_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        df['H-L'] = df['High'] - df['Low']
        df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
        df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['H-L','H-PC','L-PC']].max(axis=1)

        df['+DM'] = np.where(
            (df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']),
            df['High'] - df['High'].shift(1), 0
        )
        df['+DM'] = np.where(df['+DM'] < 0, 0, df['+DM'])

        df['-DM'] = np.where(
            (df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)),
            df['Low'].shift(1) - df['Low'], 0
        )
        df['-DM'] = np.where(df['-DM'] < 0, 0, df['-DM'])

        tr14 = df['TR'].ewm(alpha=1/period, adjust=False).mean()
        plus_dm14 = df['+DM'].ewm(alpha=1/period, adjust=False).mean()
        minus_dm14 = df['-DM'].ewm(alpha=1/period, adjust=False).mean()

        plus_di14 = 100 * (plus_dm14 / tr14)
        minus_di14 = 100 * (minus_dm14 / tr14)

        dx = (abs(plus_di14 - minus_di14) / (plus_di14 + minus_di14)) * 100
        df['ADX'] = dx.ewm(alpha=1/period, adjust=False).mean()

        return df

    # ---------------- Moving Averages ----------------
    def add_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
        df['MA7'] = df['Close'].rolling(window=7).mean()
        df['MA13'] = df['Close'].rolling(window=13).mean()
        
        df['MA100']= df['Close'].rolling(window=100).mean()
        df['MA200']= df['Close'].rolling(window=200).mean()

        return df

    # --- Run all indicator adders ---
    df = add_macd(df)
    df = add_rsi(df)
    df = add_adx(df)
    df = add_moving_averages(df)

    # --- Final Cleanup ---
    df = df[[
        'Date','Open','High','Low','Close','Volume',
        'MACD','Signal', 'MA7','MA13', 'MA100', 'MA200', 'RSI', 'ADX'
    ]]
    return df
