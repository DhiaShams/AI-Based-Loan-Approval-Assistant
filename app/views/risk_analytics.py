import streamlit as st


def render(decision_page=None):
    st.markdown("## Risk Analysis")
    st.caption("Prediction and decision policy for the current applicant assessment.")
    result = st.session_state.get("assessment_result")
    if not result:
        st.info("No assessment is available. Please run a new assessment first.")
        return

    prediction = result.get("model_prediction") or {}
    decision = result.get("decision") or {}
    if not prediction or not decision:
        st.warning("The assessment result is incomplete. Please run a new assessment.")
        return
    applicant = result.get("applicant_display", {})
    columns = st.columns(5)
    values = [
        ("Applicant", applicant.get("full_name", "Current applicant")),
        ("Prediction", prediction.get("label", "Unavailable")),
        ("Estimated Default Risk", f"{float(prediction.get('default_probability_percent', 0)):.2f}%"),
        ("Estimated Non-default Probability", f"{float(prediction.get('non_default_probability_percent', 0)):.2f}%"),
        ("Risk / Decision", f"{decision.get('risk_level', 'Unavailable')} / {decision.get('recommendation', 'Unavailable')}"),
    ]
    for column, (label, value) in zip(columns, values):
        with column:
            st.metric(label, value)

    st.divider()
    st.subheader("Assessment Summary")
    st.write("The recommendation is based on the estimated default risk and the configured decision policy.")

    if decision_page is not None and st.button("View Decision Explanation", type="primary"):
        st.switch_page(decision_page)
