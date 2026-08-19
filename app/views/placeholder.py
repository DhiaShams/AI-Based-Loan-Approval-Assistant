import streamlit as st


def render(title):
    st.markdown(f"## {title}")
    st.info(f"{title} — coming soon")
