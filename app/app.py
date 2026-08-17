"""Streamlit entry point for the AI loan approval assistant."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT_DIR / "reports" / "metrics" / "model_metrics.json"

st.set_page_config(page_title="AI Loan Approval Assistant", page_icon="🏦", layout="wide")

st.title("AI-Based Loan Approval Assistant")

pages = [
    "Dashboard",
    "New Assessment",
    "Applicant Profile",
    "Decision Explanation",
    "Model Performance",
    "Fairness Analysis",
    "Cost Analysis",
]

selection = st.sidebar.selectbox("Navigation", pages)

if selection == "Dashboard":
    st.header("Dashboard")
    st.write("Use the navigation to assess an application, review model metrics, and audit fairness.")

elif selection == "New Assessment":
    st.header("New Assessment")
    st.write("This form is intentionally limited to the features required by the trained model.")
    with st.form("loan_form"):
        applicant = {
            "loan_amnt": st.number_input("Loan Amount", min_value=0.0, value=15000.0),
            "annual_inc": st.number_input("Annual Income", min_value=0.0, value=60000.0),
            "dti": st.number_input("DTI (%)", min_value=0.0, value=15.0),
            "fico_range_low": st.number_input("FICO Score", min_value=300, max_value=850, value=700),
            "revol_util": st.number_input("Revolving Utilization (%)", min_value=0.0, value=35.0),
            "term": st.number_input("Term (months)", min_value=12, max_value=84, value=36),
            "int_rate": st.number_input("Interest Rate (%)", min_value=0.0, value=8.5),
            "emp_length": st.number_input("Employment Length (years)", min_value=0, max_value=50, value=5),
            "home_ownership": st.selectbox("Home Ownership", ["MORTGAGE", "RENT", "OWN", "OTHER", "NONE"]),
            "verification_status": st.selectbox("Verification Status", ["Verified", "Source Verified", "Not Verified"]),
            "purpose": st.selectbox("Loan Purpose", ["debt_consolidation", "credit_card", "home_improvement", "major_purchase", "medical", "other"]),
            "grade": st.selectbox("Grade", ["A", "B", "C", "D", "E", "F", "G"]),
            "sub_grade": st.selectbox("Sub Grade", ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "B4", "B5", "C1", "C2", "C3", "C4", "C5"]),
            "issue_d": st.date_input("Issue Date"),
            "earliest_cr_line": st.date_input("Earliest Credit Line"),
        }
        submitted = st.form_submit_button("Analyze Application")

    if submitted:
        from src.model.predict import predict_applicant

        outcome = predict_applicant(applicant)
        st.metric("Default Probability", f"{outcome['default_probability'] * 100:.1f}%")
        st.metric("Risk Level", outcome["risk_level"])
        st.metric("Recommendation", outcome["recommendation"])

elif selection == "Applicant Profile":
    st.header("Applicant Profile")
    st.info("This view is a placeholder for a structured profile summary that can be expanded once the deployed data contract is finalized.")

elif selection == "Decision Explanation":
    st.header("Decision Explanation")
    st.info("SHAP-backed explanation output will appear here for the selected applicant, once a model has been trained and the application is connected to that model.")

elif selection == "Model Performance":
    st.header("Model Performance")
    if METRICS_PATH.exists():
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        st.json(metrics)
    else:
        st.warning("Training metrics are not available yet. Run python src/model/train.py and python src/model/evaluate.py first.")

elif selection == "Fairness Analysis":
    st.header("Fairness Analysis")
    st.write("This audit compares performance across groups using the same held-out test split, and is intended to surface potential disparities rather than assert fairness.")

elif selection == "Cost Analysis":
    st.header("Cost Analysis")
    st.write("A false approval means the model recommends APPROVE while the true outcome is DEFAULT. The cost assumption is configurable and should be treated as a project assumption rather than a real financial loss claim.")

else:
    st.header("Overview")
    st.write("AI-Based Loan Approval Assistant")
