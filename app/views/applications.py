import streamlit as st
from utils.data import RECENT_APPLICATIONS
from utils.components import applications_table


def render():
    st.markdown("## Applications")
    st.caption("AI-powered loan decision intelligence")
    st.write("")
    show_search = st.query_params.get("search") == "1"
    applications_table(
        RECENT_APPLICATIONS,
        show_search=show_search,
        show_view_all=not show_search,
    )
