import pandas as pd
import ta
import joblib
import shap
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "technical_model.joblib")
_model = joblib.load(MODEL_PATH)
_explainer = shap.TreeExplainer(_model)

FEATURES = ["macd_diff", "atr_pct", "rsi", "roc_10", "stoch_k", "bb_pct"]

FEATURE_LABELS = {
    "macd_diff": "MACD (trend momentum)",
    "atr_pct": "Volatility (ATR)",
    "rsi": "RSI (momentum)",
    "roc_10": "10-day rate of change",
    "stoch_k": "Stochastic oscillator",
    "bb_pct": "Bollinger Band position",
}


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
    df["macd_diff"] = ta.trend.MACD(df["Close"]).macd_diff()

    bb = ta.volatility.BollingerBands(df["Close"])
    df["bb_pct"] = bb.bollinger_pband()

    stoch = ta.momentum.StochasticOscillator(df["High"], df["Low"], df["Close"])
    df["stoch_k"] = stoch.stoch()

    atr = ta.volatility.AverageTrueRange(df["High"], df["Low"], df["Close"])
    df["atr_pct"] = atr.average_true_range() / df["Close"]

    df["roc_10"] = ta.momentum.ROCIndicator(df["Close"], window=10).roc()

    return df


def technical_score_ml(df: pd.DataFrame) -> dict:
    feat_df = _build_features(df)
    latest = feat_df[FEATURES].iloc[[-1]]

    if latest.isna().any(axis=1).iloc[0]:
        return {
            "score": 0,
            "normalized": 0,
            "reasons": ["Not enough price history to compute technical indicators"],
        }

    proba_up = _model.predict_proba(latest)[0][1]
    normalized = round((proba_up - 0.5) * 2, 3)

    shap_values = _explainer.shap_values(latest)
    contributions = list(zip(FEATURES, shap_values[0]))
    contributions.sort(key=lambda x: abs(x[1]), reverse=True)

    reasons = []
    for feature, value in contributions[:3]:
        direction = "pushed prediction UP" if value > 0 else "pushed prediction DOWN"
        reasons.append(f"{FEATURE_LABELS[feature]} {direction} (SHAP value: {value:.3f})")

    return {
        "score": float(round(proba_up, 3)),
        "normalized": float(round(normalized, 3)),
        "reasons": reasons,
        "model_probability_up": float(round(proba_up, 3)),
    }