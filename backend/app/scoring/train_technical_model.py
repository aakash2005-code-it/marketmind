import yfinance as yf
import pandas as pd
import ta
import xgboost as xgb
import joblib

FEATURES = ["macd_diff", "atr_pct", "rsi", "roc_10", "stoch_k", "bb_pct"]


def build_dataset(ticker: str, period: str = "10y", horizon_days: int = 5):
    df = yf.Ticker(ticker).history(period=period)
    if df.empty or len(df) < 100:
        raise ValueError(f"Not enough data for {ticker}")

    df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
    df["macd_diff"] = ta.trend.MACD(df["Close"]).macd_diff()

    bb = ta.volatility.BollingerBands(df["Close"])
    df["bb_pct"] = bb.bollinger_pband()

    stoch = ta.momentum.StochasticOscillator(df["High"], df["Low"], df["Close"])
    df["stoch_k"] = stoch.stoch()

    atr = ta.volatility.AverageTrueRange(df["High"], df["Low"], df["Close"])
    df["atr_pct"] = atr.average_true_range() / df["Close"]

    df["roc_10"] = ta.momentum.ROCIndicator(df["Close"], window=10).roc()

    df["future_close"] = df["Close"].shift(-horizon_days)
    df["target"] = (df["future_close"] > df["Close"]).astype(int)

    df = df.dropna()
    return df


def train_model(tickers: list[str]):
    all_data = []
    for t in tickers:
        try:
            data = build_dataset(t)
            all_data.append(data)
            print(f"{t}: {len(data)} rows")
        except Exception as e:
            print(f"Skipped {t}: {e}")

    full_df = pd.concat(all_data)
    X = full_df[FEATURES]
    y = full_df["target"]

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
    )
    model.fit(X, y)

    joblib.dump(model, "app/scoring/technical_model.joblib")
    print("Model saved to app/scoring/technical_model.joblib")


if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "V", "WMT"]
    train_model(tickers)