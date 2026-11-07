import numpy as np
import pandas as pd

from app.scoring.technical_ml import _model, _build_features, FEATURES, FEATURE_LABELS

# These mirror the verdict thresholds in app/ensemble/combiner.py
BUY_THRESHOLD = 0.25
AVOID_THRESHOLD = -0.25

# Test each feature at -3.0 to +3.0 standard deviations from its current value, in 0.25 steps
STEP_GRID = [x * 0.25 for x in range(-12, 13) if x != 0]


def _verdict_from_score(final_score):
    if final_score > BUY_THRESHOLD:
        return "Buy"
    if final_score < AVOID_THRESHOLD:
        return "Avoid"
    return "Hold"


def compute_counterfactuals(df, fund_norm, sent_norm, weights, current_verdict, max_results=3):
    """Find the smallest single-indicator change that would flip the verdict."""
    w_tech, w_fund, w_sent = weights

    feat_df = _build_features(df)
    feat_clean = feat_df[FEATURES].dropna()
    if feat_clean.empty:
        return []

    latest = feat_df[FEATURES].iloc[[-1]]
    if latest.isna().any(axis=1).iloc[0]:
        return []

    stds = feat_clean.std()
    base_row = latest.iloc[0]
    candidates = []

    for feature in FEATURES:
        std = float(stds[feature])
        if std == 0 or np.isnan(std):
            continue

        rows = pd.DataFrame([base_row.values] * len(STEP_GRID), columns=FEATURES)
        rows[feature] = base_row[feature] + np.array(STEP_GRID) * std
        probas = _model.predict_proba(rows)[:, 1]

        best = None
        for step, p in zip(STEP_GRID, probas):
            tech_norm = (float(p) - 0.5) * 2
            final = w_tech * tech_norm + w_fund * fund_norm + w_sent * sent_norm
            new_verdict = _verdict_from_score(final)
            if new_verdict != current_verdict:
                if best is None or abs(step) < abs(best[0]):
                    best = (step, new_verdict, float(base_row[feature] + step * std))

        if best:
            step, new_verdict, new_value = best
            current_value = float(base_row[feature])
            candidates.append({
                "feature": feature,
                "label": FEATURE_LABELS[feature],
                "current_value": round(current_value, 3),
                "needed_value": round(new_value, 3),
                "change_size_std": round(abs(step), 2),
                "flips_to": new_verdict,
                "sentence": (
                    f"If {FEATURE_LABELS[feature]} moved from {current_value:.2f} "
                    f"to {new_value:.2f}, the verdict would change from "
                    f"{current_verdict} to {new_verdict}."
                ),
            })

    candidates.sort(key=lambda c: c["change_size_std"])
    return candidates[:max_results]