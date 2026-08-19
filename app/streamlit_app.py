from PIL import Image
import streamlit as st
from utils.styles import inject_custom_css
from utils.components import sidebar_brand, sidebar_user_footer, sidebar_spacer, sidebar_nav_link
from utils.data import CURRENT_USER
from utils.icons import ICONS_DIR
from views import dashboard, new_assessment, applications, risk_analytics, placeholder,decision_explanation,fairness

st.set_page_config(
    page_title="Loan AI — Decision Intelligence",
    page_icon=Image.open(ICONS_DIR / "loan_ai.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

# Read applicant query parameter globally to set session state with change-detection
qp = st.query_params
if "applicant" in qp:
    val = qp["applicant"]
    if st.session_state.get("last_seen_applicant_qp") != val:
        st.session_state["selected_applicant_name"] = val
        st.session_state["last_seen_applicant_qp"] = val

dashboard_page = st.Page(dashboard.render, title="Dashboard", url_path="dashboard", default=True)
applications_page = st.Page(applications.render, title="Applications", url_path="applications")
risk_analytics_page = st.Page(risk_analytics.render, title="Risk Analytics", url_path="risk-analytics")
new_assessment_page = st.Page(
    lambda: new_assessment.render(risk_analytics_page),
    title="New Assessment",
    url_path="new-assessment",
)
decision_explanation_page = st.Page(decision_explanation.render, title="Decision Explanation",url_path="decision-explanation")
fairness_page = st.Page(
    lambda: fairness.render(dashboard_page),
    title="Fairness",
    url_path="fairness",
)
settings_page = st.Page(lambda: placeholder.render("Settings"), title="Settings", url_path="settings")

# Each main-nav page paired with its icon filename (icons/<name>.png).
# st.Page's own `icon` param only accepts emoji/Material Symbols, so the
# custom icons are applied via sidebar_nav_link() below instead.
main_nav_pages = [
    (dashboard_page, "dashboard"),
    (new_assessment_page, "new_assessment"),
    (applications_page, "applications"),
    (risk_analytics_page, "risk_analysis"),
    (decision_explanation_page, "decision_explanation"),
    (fairness_page, "fairness"),
]
all_pages = [page for page, _ in main_nav_pages] + [settings_page]

# position="hidden" suppresses Streamlit's built-in nav widget, which always
# pins itself to the very top of the sidebar regardless of code order. We
# render our own nav links instead, so we control exact placement (logo at
# the top, main nav below it, settings + profile pinned to the bottom) and
# can use our own PNG icons instead of Streamlit's emoji/Material set.
pg = st.navigation(all_pages, position="hidden")

with st.sidebar:
    sidebar_brand()

    for page, icon_name in main_nav_pages:
        sidebar_nav_link(page, icon_name, active=(pg.url_path == page.url_path))

    sidebar_spacer()

    st.divider()
    sidebar_nav_link(settings_page, "settings", active=(pg.url_path == settings_page.url_path))
    sidebar_user_footer(CURRENT_USER)

pg.run()
