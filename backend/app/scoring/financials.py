import yfinance as yf


def get_quarterly_financials(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        income = stock.quarterly_financials

        if income is None or income.empty:
            return {"quarters": []}

        # Revenue and Net Income rows (yfinance labels vary slightly by company)
        revenue_row = None
        net_income_row = None
        for label in ["Total Revenue", "Revenue"]:
            if label in income.index:
                revenue_row = income.loc[label]
                break
        for label in ["Net Income", "Net Income Common Stockholders"]:
            if label in income.index:
                net_income_row = income.loc[label]
                break

        if revenue_row is None:
            return {"quarters": []}

        quarters = []
        # Take up to the last 4 quarters, oldest first
        cols = list(income.columns)[:4][::-1]
        for col in cols:
            revenue = revenue_row.get(col)
            net_income = net_income_row.get(col) if net_income_row is not None else None
            quarters.append({
                "label": col.strftime("%b %Y"),
                "revenue_millions": round(revenue / 1_000_000, 1) if revenue else None,
                "net_income_millions": round(net_income / 1_000_000, 1) if net_income else None,
            })

        return {"quarters": quarters}
    except Exception:
        return {"quarters": []}