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
        "decision": "approve",
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
