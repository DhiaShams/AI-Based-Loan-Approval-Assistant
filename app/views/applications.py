import streamlit as st
from utils.data import RECENT_APPLICATIONS
from utils.components import applications_table


def render():
    st.markdown("## Applications")
    st.caption("AI-powered loan decision intelligence")
    st.write("")
    applications_table(RECENT_APPLICATIONS)
