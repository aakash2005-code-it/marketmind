import pandas as pd
import ta

def technical_score(df: pd.DataFrame) -> dict:
    df = df.copy()

    df["rsi"] = ta.momentum.RSIIndicator(close=df["Close"]).rsi()
    df["macd_diff"] = ta.trend.MACD(close=df["Close"]).macd_diff()
    df["sma50"] = df["Close"].rolling(window=50).mean()

    latest = df.iloc[-1]
    score = 0
    reasons = []

    # RSI signal
    rsi = latest["rsi"]
    if pd.notna(rsi):
        if rsi < 30:
            score += 1
            reasons.append(f"RSI is {rsi:.1f}, indicating the stock is oversold")
        elif rsi > 70:
            score -= 1
            reasons.append(f"RSI is {rsi:.1f}, indicating the stock is overbought")
        else:
            reasons.append(f"RSI is {rsi:.1f}, in a neutral range")

    # MACD signal
    macd_diff = latest["macd_diff"]
    if pd.notna(macd_diff):
        if macd_diff > 0:
            score += 1
            reasons.append("MACD shows bullish momentum")
        else:
            score -= 1
            reasons.append("MACD shows bearish momentum")

    # Moving average signal
    sma50 = latest["sma50"]
    close = latest["Close"]
    if pd.notna(sma50):
        if close > sma50:
            score += 1
            reasons.append(f"Price (${close:.2f}) is above the 50-day moving average (${sma50:.2f})")
        else:
            score -= 1
            reasons.append(f"Price (${close:.2f}) is below the 50-day moving average (${sma50:.2f})")

    max_score = 3

    return {
        "score": score,
        "max_score": max_score,
        "normalized": round(score / max_score, 2),
        "reasons": reasons,
    }