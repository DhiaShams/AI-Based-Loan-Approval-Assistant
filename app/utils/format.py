def format_currency(amount):
    return f"\u20b9{amount:,.0f}"


def risk_level_label(level):
    return {"low": "Low Risk", "medium": "Medium Risk", "high": "High Risk"}[level]


def decision_label(decision):
    return {"approve": "Approve", "review": "Review", "reject": "Reject"}[decision]


def credit_score_rating(score):
    score = float(score)
    if score >= 750:
        return "Excellent"
    if score >= 700:
        return "Good"
    if score >= 650:
        return "Fair"
    return "Poor"


def debt_to_income_ratio(existing_debt, annual_income):
    if not annual_income:
        return 0.0
    return round((existing_debt / annual_income) * 100)
