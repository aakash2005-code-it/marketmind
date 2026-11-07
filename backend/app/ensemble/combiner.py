def combine_scores(technical: dict, fundamentals: dict, sentiment: dict,
                    weights: tuple = (0.4, 0.3, 0.3)) -> dict:
    tech_norm = technical["normalized"]
    fund_norm = fundamentals["normalized"]
    sent_norm = sentiment["normalized"]

    w_tech, w_fund, w_sent = weights
    final_score = (w_tech * tech_norm) + (w_fund * fund_norm) + (w_sent * sent_norm)
    final_score = round(final_score, 3)

    if final_score > 0.25:
        verdict = "Buy"
        risk_level = "Low" if final_score > 0.5 else "Medium"
    elif final_score < -0.25:
        verdict = "Avoid"
        risk_level = "Low" if final_score < -0.5 else "Medium"
    else:
        verdict = "Hold"
        risk_level = "Medium"

    confidence = round(min(abs(final_score) * 2, 1.0), 2)

    explanation = []
    explanation.extend([f"[Technical] {r}" for r in technical["reasons"]])
    explanation.extend([f"[Fundamental] {r}" for r in fundamentals["reasons"]])
    explanation.extend([f"[Sentiment] {r}" for r in sentiment["reasons"]])

    return {
        "verdict": verdict,
        "investment_score": final_score,
        "confidence_score": confidence,
        "risk_level": risk_level,
        "breakdown": {
            "technical": tech_norm,
            "fundamental": fund_norm,
            "sentiment": sent_norm,
            "weights_used": {"technical": w_tech, "fundamental": w_fund, "sentiment": w_sent},
        },
        "explanation": explanation,
    }