import streamlit as st


DISPLAY_NAMES = {
    "loan_amnt": "Loan Amount", "term": "Loan Term", "int_rate": "Interest Rate",
    "installment": "Monthly Installment", "emp_length": "Employment Length",
    "home_ownership": "Home Ownership", "annual_inc": "Annual Income",
    "verification_status": "Verification Status", "issue_d": "Loan Issue Date",
    "purpose": "Loan Purpose", "dti": "Debt-to-Income Ratio",
    "delinq_2yrs": "Delinquencies (Last 2 Years)", "earliest_cr_line": "Earliest Credit Line",
    "fico_range_low": "FICO Score (Low)", "fico_range_high": "FICO Score (High)",
    "inq_last_6mths": "Credit Inquiries (Last 6 Months)",
    "mths_since_last_delinq": "Months Since Last Delinquency",
    "mths_since_last_record": "Months Since Last Public Record", "open_acc": "Open Credit Accounts",
    "pub_rec": "Public Records", "revol_bal": "Revolving Balance",
    "revol_util": "Revolving Credit Utilization", "total_acc": "Total Credit Accounts",
    "acc_now_delinq": "Current Delinquencies", "tot_coll_amt": "Total Collection Amount",
    "tot_cur_bal": "Total Current Balance", "mort_acc": "Mortgage Accounts",
    "pub_rec_bankruptcies": "Public Record Bankruptcies", "tax_liens": "Tax Liens",
    "initial_list_status": "Initial Listing Status", "application_type": "Application Type",
    "credit_history_years": "Credit History Length",
    "emp_length_missing": "Employment Length",
    "mths_since_last_delinq_missing": "Months Since Last Delinquency",
    "mths_since_last_record_missing": "Months Since Last Public Record",
}

ONE_HOT_PREFIXES = {
    "home_ownership_": "home_ownership", "verification_status_": "verification_status",
    "purpose_": "purpose", "initial_list_status_": "initial_list_status",
    "application_type_": "application_type",
}


def _feature_details(factor, applicant):
    feature = factor.get("feature", "")
    raw_feature = feature
    selected_value = applicant.get(feature)
    for prefix, base_feature in ONE_HOT_PREFIXES.items():
        if feature.startswith(prefix):
            raw_feature = base_feature
            selected_value = applicant.get(base_feature, feature[len(prefix):])
            break
    return DISPLAY_NAMES.get(raw_feature, factor.get("display_name", "This factor")), selected_value


def _format_value(feature, value):
    if value is None:
        return "Not provided"
    if feature in {"Loan Amount", "Annual Income", "Monthly Installment", "Revolving Balance", "Total Collection Amount", "Total Current Balance"}:
        return f"${float(value):,.0f}"
    if feature in {"Interest Rate", "Debt-to-Income Ratio", "Revolving Credit Utilization"}:
        return f"{float(value):,.1f}%"
    if feature == "Loan Term":
        return f"{float(value):,.0f} months"
    if feature in {"Employment Length", "Open Credit Accounts", "Total Credit Accounts", "Mortgage Accounts", "Public Records", "Public Record Bankruptcies", "Tax Liens", "Current Delinquencies", "Delinquencies (Last 2 Years)", "Credit Inquiries (Last 6 Months)"}:
        return f"{float(value):,.0f}"
    return str(value)


def _render_factors(title, factors, applicant, color):
    st.markdown(f"### {title}")
    if not factors:
        st.caption("No applicant factors in this category.")
        return
    for index, factor in enumerate(factors[:5], 1):
        label, value = _feature_details(factor, applicant)
        feature_value = _format_value(label, value)
        direction = "higher" if float(factor.get("shap_value", 0)) > 0 else "lower"
        explanation = f"Your {label} of {feature_value} is contributing to {direction} estimated default risk."
        st.markdown(
            f"**{index}. {label}**  \n"
            f"Applicant value: **{feature_value}**  \n"
            f":{color}[{explanation}]"
        )
        st.divider()


def _summary(increasing, reducing, applicant):
    increasing_names = [_feature_details(factor, applicant)[0] for factor in increasing[:3]]
    reducing_names = [_feature_details(factor, applicant)[0] for factor in reducing[:3]]
    sentences = []
    if increasing_names:
        joined = ", ".join(increasing_names[:-1]) + (f" and {increasing_names[-1]}" if len(increasing_names) > 1 else increasing_names[-1])
        sentences.append(f"Your assessment was influenced by {joined}, which contributed to higher estimated default risk.")
    if reducing_names:
        joined = ", ".join(reducing_names[:-1]) + (f" and {reducing_names[-1]}" if len(reducing_names) > 1 else reducing_names[-1])
        sentences.append(f"{joined} helped reduce the estimated risk.")
    return " ".join(sentences)


def render():
    st.markdown("## Decision Explanation")
    st.markdown("### Why was this prediction made?")
    result = st.session_state.get("assessment_result")
    if not result:
        st.info("No assessment is available. Please run a new assessment first.")
        return

    prediction = result.get("model_prediction") or {}
    decision = result.get("decision") or {}
    explanation = result.get("explanation") or {}
    applicant = result.get("applicant") or {}
    if not prediction or not decision:
        st.warning("The assessment result is incomplete. Please run a new assessment.")
        return

    st.markdown(f"Your application was classified as **{str(prediction.get('label', 'Unknown')).upper()}**.")
    columns = st.columns(4)
    values = [
        ("Estimated Default Risk", f"{float(prediction.get('default_probability_percent', 0)):.2f}%"),
        ("Estimated Non-default Probability", f"{float(prediction.get('non_default_probability_percent', 0)):.2f}%"),
        ("Risk Level", str(decision.get("risk_level", "Unknown")).upper()),
        ("Recommendation", str(decision.get("recommendation", "Unknown")).upper()),
    ]
    for column, (label, value) in zip(columns, values):
        with column:
            st.metric(label, value)

    increasing = explanation.get("top_risk_factors") or explanation.get("risk_factors") or []
    reducing = explanation.get("top_protective_factors") or explanation.get("protective_factors") or []
    if not increasing and not reducing:
        st.info("Prediction is available, but the detailed explanation could not be generated.")
        return

    st.caption("These are the factors that had the strongest influence on this individual prediction.")
    _render_factors("Factors Increasing Default Risk", increasing, applicant, "red")
    _render_factors("Factors Reducing Default Risk", reducing, applicant, "green")
    st.markdown("### What influenced your result?")
    st.write(_summary(increasing, reducing, applicant))
