
SECTOR_AVG_PE = {
    "TECHNOLOGY": 30,
    "HEALTHCARE": 25,
    "FINANCIAL SERVICES": 15,
    "ENERGY": 12,
    "CONSUMER CYCLICAL": 22,
    "CONSUMER DEFENSIVE": 20,
    "INDUSTRIALS": 20,
    "UTILITIES": 18,
    "REAL ESTATE": 18,
    "COMMUNICATION SERVICES": 20,
    "BASIC MATERIALS": 15,
}
DEFAULT_SECTOR_PE = 20


def fundamentals_score(fundamentals: dict) -> dict:
    score = 0
    max_score = 2
    reasons = []

    pe_ratio = fundamentals.get("pe_ratio")
    sector = (fundamentals.get("sector") or "").upper()
    debt_to_equity = fundamentals.get("debt_to_equity")

    sector_avg_pe = SECTOR_AVG_PE.get(sector, DEFAULT_SECTOR_PE)

    # P/E signal
    if pe_ratio is not None:
        if pe_ratio < sector_avg_pe:
            score += 1
            reasons.append(f"P/E ratio ({pe_ratio:.1f}) is below the {sector.title() or 'market'} sector average (~{sector_avg_pe})")
        else:
            score -= 1
            reasons.append(f"P/E ratio ({pe_ratio:.1f}) is above the {sector.title() or 'market'} sector average (~{sector_avg_pe})")
    else:
        reasons.append("P/E ratio unavailable")

    # Debt-to-equity signal
    if debt_to_equity is not None:
        if debt_to_equity < 100:
            score += 1
            reasons.append(f"Debt-to-equity ({debt_to_equity:.1f}) indicates manageable leverage")
        else:
            score -= 1
            reasons.append(f"Debt-to-equity ({debt_to_equity:.1f}) indicates high leverage")
    else:
        max_score -= 1  # don't penalize for missing data, just reduce max
        reasons.append("Debt-to-equity ratio unavailable")

    normalized = round(score / max_score, 2) if max_score > 0 else 0

    return {
        "score": score,
        "max_score": max_score,
        "normalized": normalized,
        "reasons": reasons,
    }