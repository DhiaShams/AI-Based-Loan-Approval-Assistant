import streamlit as st
from utils.data import SUMMARY_STATS, RECENT_APPLICATIONS, CURRENT_USER
from utils.components import stat_card, applications_table


def render():
    first_name = CURRENT_USER["name"].split()[0]
    st.markdown(f"## Good morning, {first_name}")
    st.caption("AI-powered loan decision intelligence")

    col1, col2, col3 = st.columns(3)
    with col1:
        stat_card("APPLICATIONS", f"{SUMMARY_STATS['applications']:,}")
    with col2:
        stat_card("AVERAGE RISK", f"{SUMMARY_STATS['average_risk']}%")
    with col3:
        stat_card("HIGH RISK", str(SUMMARY_STATS["high_risk"]))

    st.write("")
    applications_table(RECENT_APPLICATIONS, show_search=False, show_view_all=True)
