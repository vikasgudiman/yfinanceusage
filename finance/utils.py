# utils.py

def get_rsi_color(value):
    """Return color + label for RSI"""
    if value < 30:
        return "lightred", "Sell"
    elif value > 80:
        return "darkred", "Strong Sell"
    elif value >= 70:
        return "lightred", "Sell"
    elif value > 55:
        return "lightgreen", "Buy"
    else:
        return "gray", "Neutral"


def get_adx_color(value):
    """Return color + label for ADX"""
    if value < 20:
        return "lightred", "Sell"
    elif value > 30:
        return "darkgreen", "Strong Buy"
    elif value > 20:
        return "lightgreen", "Buy"
    else:
        return "gray", "Neutral"


def get_ma_color(ma13, ma7):
    """Return color + label for MA13/MA7"""
    if ma13 > ma7:
        return "lightgreen", "Buy"
    else:
        return "lightred", "Sell"


def get_ma100_200_color(ma100, ma200):
    """Return color + label for MA100/MA200"""
    if ma200 > ma100:
        return "lightgreen", "Buy"
    else:
        return "lightred", "Sell"


def get_price_vs_ma100_200_color(price, ma100, ma200):
    """Return color + label for price vs MA100 & MA200"""
    if price > ma100 and price > ma200:
        return "darkgreen", "Strong Buy"
    elif ma200 > ma100:
        return "lightgreen", "Buy"
    else:
        return "lightred", "Sell"


def get_macd_signal_color(macd, signal):
    """Return color + label for MACD/Signal"""
    if macd > signal and macd > 0 and signal > 0:
        return "darkgreen", "Strong Buy"
    elif macd == signal:
        return "gray", "Neutral"
    elif macd < signal and macd < 0 and signal < 0:
        return "darkred", "Strong Sell"
    elif macd < signal:
        return "lightred", "Sell"
    else:
        return "lightgreen", "Buy"


def build_macd_signal_key(macd, signal):
    color, label = get_macd_signal_color(macd, signal)
    return {"key": "MACD/Signal", "value": [[macd, signal], color, label]}


def get_color(key, value):
    """Assigns color and label for individual keys"""
    if key == "RSI":
        return get_rsi_color(value)
    elif key == "ADX":
        return get_adx_color(value)
    elif key == "MACD":
        return ("darkgreen", "Strong Buy") if value > 0 else ("darkred", "Strong Sell") if value < 0 else ("gray", "Neutral")
    elif key == "Signal":
        return ("lightgreen", "Buy") if value > 0 else ("lightred", "Sell") if value < 0 else ("gray", "Neutral")
    else:
        return "gray", "Neutral"
