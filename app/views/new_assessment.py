import streamlit as st
from utils.format import credit_score_rating, debt_to_income_ratio
from utils.components import risk_badge_html, decision_html, render_html, card_heading


# The application currently under review.
# In production, this would be loaded using an application ID.
APPLICATION_UNDER_REVIEW = {
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
}


def mock_risk_assessment(credit_score, dti_pct, previous_delays):
    """Placeholder heuristic - replace with the real model prediction
    endpoint once it is ready."""

    score = 0
    score += max(0, (700 - credit_score)) * 0.25
    score += dti_pct * 0.8
    score += previous_delays * 8
    score = max(1, min(99, round(score)))

    if score < 35:
        level, decision = "low", "approve"
    elif score < 65:
        level, decision = "medium", "review"
    else:
        level, decision = "high", "reject"

    return score, level, decision


def field_row(label, value, suffix=""):
    """Render a read-only application field."""
    render_html(f"""
        <p class="field-label">{label}</p>
        <div class="field-box">{value}{suffix}</div>
    """)


def render():
    fields = APPLICATION_UNDER_REVIEW

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------
    st.markdown("## New Loan Assessment")
    st.caption("Reviewing application")

    # ---------------------------------------------------------
    # Applicant Information + Financial Profile
    # ---------------------------------------------------------
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        with st.container(border=True):
            card_heading("application_info", "Applicant Information")

            field_row("Full Name", fields["full_name"])

            c1, c2 = st.columns(2)

            with c1:
                field_row("Age", fields["age"])

            with c2:
                field_row("Employment Length", fields["employment_length"])

            field_row("Home Ownership", fields["home_ownership"])

    with row1_col2:
        with st.container(border=True):
            card_heading("financial_profile", "Financial Profile")

            c1, c2 = st.columns(2)

            with c1:
                field_row("Annual Income", fields["annual_income"])

            with c2:
                field_row("Loan Amount", fields["loan_amount"])

            field_row("Existing Debt", fields["existing_debt"])

            dti_pct = debt_to_income_ratio(
                fields["existing_debt"],
                fields["annual_income"]
            )

            field_row("Debt-to-Income Ratio", f"{dti_pct}%")

    # ---------------------------------------------------------
    # Credit Profile + Loan Details
    # ---------------------------------------------------------
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        with st.container(border=True):
            card_heading("credit_profile", "Credit Profile")

            rating = credit_score_rating(fields["credit_score"])

            render_html(f"""
                <p class="field-label">Credit Rating</p>
                <div class="field-box">
                    <span style="font-weight:700;">
                        {fields['credit_score']}
                    </span>
                    <span style="color:#16a34a; font-weight:600;">
                        ({rating})
                    </span>
                </div>
            """)

            c1, c2 = st.columns(2)

            with c1:
                field_row("Credit History", fields["credit_history"])

            with c2:
                field_row("Previous Delays", fields["previous_delays"])

    with row2_col2:
        with st.container(border=True):
            card_heading("loan_details", "Loan Details")

            field_row("Loan Purpose", fields["loan_purpose"])
            field_row("Repayment Term", fields["repayment_term"])

    # ---------------------------------------------------------
    # Run Assessment
    # ---------------------------------------------------------
    st.write("")

    footer_col, button_col = st.columns([3, 1])

    with footer_col:
        st.caption(
            "✨ AI metrics are generated dynamically using "
            "fairness-evaluated models."
        )

    with button_col:
        run_clicked = st.button(
            "▶ Run AI Assessment",
            type="primary",
            use_container_width=True
        )

    # ---------------------------------------------------------
    # Assessment
    # ---------------------------------------------------------
    if run_clicked:
        dti_pct = debt_to_income_ratio(
            fields["existing_debt"],
            fields["annual_income"]
        )

        score, level, decision = mock_risk_assessment(
            fields["credit_score"],
            dti_pct,
            fields["previous_delays"]
        )

        st.session_state["last_assessment"] = {
            "applicant": fields["full_name"],
            "score": score,
            "level": level,
            "decision": decision,
        }

    # ---------------------------------------------------------
    # Assessment Result
    # ---------------------------------------------------------
    if "last_assessment" in st.session_state:
        result = st.session_state["last_assessment"]

        st.write("")

        with st.container(border=True):
            st.markdown("**Assessment Result**")

            r1, r2, r3 = st.columns(3)

            with r1:
                st.markdown(
                    f"Applicant: **{result['applicant']}**"
                )

            with r2:
                st.markdown(
                    f"Risk Score: **{result['score']}%**"
                )

            with r3:
                render_html(
                    f"{risk_badge_html(result['level'])} "
                    f"&nbsp; "
                    f"{decision_html(result['decision'])}"
                )

        st.caption(
            "Placeholder scoring logic - replace "
            "`mock_risk_assessment` with a call to the real model endpoint."
        )