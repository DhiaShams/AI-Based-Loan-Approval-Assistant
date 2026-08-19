"""
Placeholder data. Swap `RECENT_APPLICATIONS` and `SUMMARY_STATS` for real
model/backend output once ready - shapes are kept close to expected model
output (risk_score, risk_level, decision) so wiring in real data later is
a data-source swap, not a page rewrite.
"""

SUMMARY_STATS = {
    "applications": 1248,
    "average_risk": 31.4,  # percent
    "high_risk": 186,
}

RECENT_APPLICATIONS = [
    {
        "id": "APP-1001",
        "applicant": "Arjun Menon",
        "amount": 500000,
        "risk_score": 18,
        "risk_level": "low",
        "decision": "pending",
    },
    {
        "id": "APP-1002",
        "applicant": "Sarah Thomas",
        "amount": 800000,
        "risk_score": 64,
        "risk_level": "medium",
        "decision": "review",
    },
    {
        "id": "APP-1003",
        "applicant": "Rahul Kumar",
        "amount": 300000,
        "risk_score": 82,
        "risk_level": "high",
        "decision": "reject",
    },
    {
        "id": "APP-1004",
        "applicant": "Ananya Nair",
        "amount": 450000,
        "risk_score": 23,
        "risk_level": "low",
        "decision": "approve",
    },
]

APPLICANT_PROFILES = {
    "Arjun Menon": {
        "full_name": "Arjun Menon",
        "age": 32,
        "employment_length": "5 years",
        "home_ownership": "RENT",
        "annual_income": 60000,
        "loan_amount": 500000,
        "existing_debt": 10000,
        "credit_score": 720,
        "credit_history": "Good",
        "previous_delays": 0,
        "loan_purpose": "Personal",
        "repayment_term": "36 Months",
    },
    "Sarah Thomas": {
        "full_name": "Sarah Thomas",
        "age": 28,
        "employment_length": "2 years",
        "home_ownership": "RENT",
        "annual_income": 80000,
        "loan_amount": 800000,
        "existing_debt": 25000,
        "credit_score": 680,
        "credit_history": "Fair",
        "previous_delays": 1,
        "loan_purpose": "Debt consolidation",
        "repayment_term": "48 Months",
    },
    "Rahul Kumar": {
        "full_name": "Rahul Kumar",
        "age": 45,
        "employment_length": "10+ years",
        "home_ownership": "MORTGAGE",
        "annual_income": 120000,
        "loan_amount": 300000,
        "existing_debt": 85000,
        "credit_score": 590,
        "credit_history": "Poor",
        "previous_delays": 3,
        "loan_purpose": "Business",
        "repayment_term": "60 Months",
    },
    "Ananya Nair": {
        "full_name": "Ananya Nair",
        "age": 35,
        "employment_length": "8 years",
        "home_ownership": "OWN",
        "annual_income": 95000,
        "loan_amount": 450000,
        "existing_debt": 5000,
        "credit_score": 750,
        "credit_history": "Excellent",
        "previous_delays": 0,
        "loan_purpose": "Home improvement",
        "repayment_term": "24 Months",
    },
}

CURRENT_USER = {
    "name": "Alex Johnson",
    "role": "Senior Loan Officer",
}

HOME_OWNERSHIP_OPTIONS = ["RENT", "OWN", "MORTGAGE", "OTHER"]
LOAN_PURPOSE_OPTIONS = [
    "Personal",
    "Debt consolidation",
    "Home improvement",
    "Business",
    "Education",
    "Medical",
]
REPAYMENT_TERM_OPTIONS = ["12 Months", "24 Months", "36 Months", "48 Months", "60 Months"]

