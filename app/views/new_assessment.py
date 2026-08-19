import json
import logging

import numpy as np
import streamlit as st

from utils.components import card_heading, render_html
from utils.credit_report import CREDIT_REPORT_FIELDS, parse_credit_report
from utils.lender_config import LENDER_VALUES
from src.explainability.applicant_features import build_model_input
from src.explainability.shap_explainer import explain_applicant, get_model


LOGGER = logging.getLogger(__name__)


PURPOSE_OPTIONS = [
    "credit_card", "debt_consolidation", "educational", "home_improvement",
    "house", "major_purchase", "medical", "moving", "other",
    "renewable_energy", "small_business", "vacation", "wedding",
]


def _field_value(label, value):
    st.markdown(f"**{label}:** {value}")


def render(risk_page):
    st.markdown("## New Loan Assessment")
    st.caption("Enter applicant information and upload the credit report required for this assessment.")

    with st.container(border=True):
        card_heading("application_info", "Applicant Details")
        applicant_col1, applicant_col2 = st.columns(2)
        with applicant_col1:
            full_name = st.text_input("Full Name", key="assessment_full_name")
            age = st.number_input("Age", min_value=18, max_value=100, value=32, step=1, key="assessment_age")
        with applicant_col2:
            employment_length = st.selectbox(
                "Employment Length",
                ["< 1 year", *[f"{year} years" for year in range(1, 10)], "10+ years"],
                index=5,
                key="assessment_emp_length",
            )
            home_ownership = st.selectbox(
                "Home Ownership", ["RENT", "MORTGAGE", "OWN", "NONE", "OTHER"], key="assessment_home"
            )

    with st.container(border=True):
        card_heading("loan_details", "Application Form")
        col1, col2, col3 = st.columns(3)
        with col1:
            loan_amnt = st.number_input("Loan Amount", min_value=1.0, value=15000.0, step=500.0)
            term = st.selectbox("Loan Term", [36, 60], format_func=lambda value: f"{value} months")
            annual_inc = st.number_input("Annual Income", min_value=1.0, value=60000.0, step=1000.0)
        with col2:
            purpose = st.selectbox("Loan Purpose", PURPOSE_OPTIONS)
            dti = st.number_input("Debt-to-Income Ratio (%)", min_value=0.0, max_value=100.0, value=20.0, step=0.5)
            application_type = st.selectbox("Application Type", ["Individual", "Joint App"])
        with col3:
            installment = st.number_input("Monthly Installment", min_value=0.0, value=500.0, step=10.0)
            st.markdown("**Applicant fields sent to model**")
            st.caption("Age and full name are display-only and are never sent to XGBoost.")

    with st.container(border=True):
        card_heading("credit_profile", "Credit Report")
        uploaded_report = st.file_uploader("Upload Credit Report TXT", type=["txt"])
        credit_values = None
        if uploaded_report is not None:
            try:
                credit_values = parse_credit_report(uploaded_report)
                st.success("Credit report parsed successfully.")
                summary_cols = st.columns(3)
                for index, field in enumerate(CREDIT_REPORT_FIELDS):
                    with summary_cols[index % 3]:
                        _field_value(field.replace("_", " ").title(), credit_values[field])
            except ValueError as error:
                st.error(str(error))

    with st.container(border=True):
        card_heading("financial_profile", "Bank / Lender Information")
        st.caption("These values are predefined for this single-lender prototype and are read-only.")
        lender_cols = st.columns(4)
        lender_labels = {
            "int_rate": "Interest Rate",
            "verification_status": "Verification Status",
            "initial_list_status": "Initial List Status",
            "issue_d": "Issue Date",
        }
        for column, field in zip(lender_cols, lender_labels):
            with column:
                st.metric(lender_labels[field], LENDER_VALUES[field])

    if st.button("Run Assessment", type="primary", use_container_width=True):
        if not full_name.strip():
            st.error("Please provide the applicant's full name.")
            return
        if credit_values is None:
            st.error("Please upload a valid credit report before running the assessment.")
            return
        applicant_data = {
            "loan_amnt": loan_amnt,
            "term": term,
            "int_rate": LENDER_VALUES["int_rate"],
            "installment": installment,
            "emp_length": employment_length,
            "home_ownership": home_ownership,
            "annual_inc": annual_inc,
            "verification_status": LENDER_VALUES["verification_status"],
            "issue_d": LENDER_VALUES["issue_d"],
            "purpose": purpose,
            "dti": dti,
            "earliest_cr_line": credit_values.pop("earliest_cr_line"),
            "initial_list_status": LENDER_VALUES["initial_list_status"],
            "application_type": application_type,
            **credit_values,
        }
        try:
            model = get_model()
            model_input, normalized = build_model_input(applicant_data, model)
            model_features = list(model.feature_names_in_)
            if list(model_input.columns) != model_features or model_input.shape != (1, len(model_features)):
                raise ValueError("Applicant data does not match the XGBoost model feature schema.")
            if model_input.isna().any().any() or not np.isfinite(model_input.to_numpy(dtype=float)).all():
                raise ValueError("Applicant data contains missing or invalid numeric values.")
            result = explain_applicant(applicant_data)
            result["applicant_display"] = {"full_name": full_name, "age": age}
            result["model_input"] = model_input.iloc[0].to_dict()
            result["normalized_applicant"] = normalized
            st.session_state["assessment_result"] = json.loads(json.dumps(result, default=str))
            st.session_state["selected_applicant_name"] = full_name
            st.switch_page(risk_page)
        except (ValueError, TypeError) as error:
            st.error(str(error))
        except Exception:
            LOGGER.exception("Loan assessment failed during model integration.")
            st.error("We could not complete this assessment. Please review the entered information and try again.")
