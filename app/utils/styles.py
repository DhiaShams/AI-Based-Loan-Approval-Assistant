import streamlit as st

CUSTOM_CSS = """
<style>
/* Tighten default Streamlit page padding */
.block-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* Card look for our custom HTML components */
.loanai-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 8px;
}

.loanai-card-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #94a3b8;
    margin: 0 0 6px 0;
}

.loanai-card-value {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.01em;
    color: #0f172a;
    margin: 0;
    line-height: 1.2;
}

/* Applications table */
.loanai-table-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}
.loanai-table-title {
    font-size: 0.98rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
}
.loanai-view-all,
.loanai-view-all:link,
.loanai-view-all:visited {
    font-size: 0.82rem;
    font-weight: 600;
    color: #2563eb !important;
    text-decoration: none !important;
}
.loanai-table-scroll {
    overflow-x: auto;
}
.loanai-table {
    width: 100%;
    border-collapse: collapse;
}
.loanai-table th {
    text-align: left;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #94a3b8;
    padding: 0 16px 10px 16px;
    border-bottom: 1px solid #f1f5f9;
}
.loanai-table th:first-child,
.loanai-table td:first-child {
    padding-left: 4px;
}
.loanai-table th:last-child,
.loanai-table td:last-child {
    padding-right: 4px;
}
.loanai-table td {
    padding: 14px 16px;
    font-size: 0.88rem;
    color: #334155;
    border-bottom: 1px solid #f8fafc;
    white-space: nowrap;
}
.loanai-table td.applicant {
    font-weight: 600;
    color: #0f172a;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
}
.badge-low { background: #dcfce7; color: #16a34a; }
.badge-medium { background: #fef3c7; color: #d97706; }
.badge-high { background: #fee2e2; color: #dc2626; }

.decision {
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}
.decision::before {
    content: "\\25CF";
    font-size: 0.6rem;
    margin-right: 6px;
}
.decision-approve { color: #16a34a; }
.decision-review { color: #d97706; }
.decision-reject { color: #dc2626; }

/* Sidebar branding block */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 4px 18px 4px;
}
.sidebar-brand-icon {
    width: 34px;
    height: 34px;
    border-radius: 9px;
    flex-shrink: 0;
}
.sidebar-brand-title {
    color: #ffffff;
    font-weight: 700;
    font-size: 0.92rem;
    line-height: 1.1;
    margin: 0;
}
.sidebar-brand-subtitle {
    color: #64748b;
    font-size: 0.6rem;
    letter-spacing: 0.06em;
    margin: 0;
}

.sidebar-user {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 4px 4px 4px;
}
.sidebar-avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
}
.sidebar-user-name {
    color: #f1f5f9;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 0;
}
.sidebar-user-role {
    color: #64748b;
    font-size: 0.72rem;
    margin: 0;
}

/* Pushes the settings link + user footer to the bottom of the sidebar.
   min-height: 100vh (not height: 100%) because stSidebarUserContent does
   not reliably inherit a percentage height from its ancestors. */
[data-testid="stSidebarUserContent"] {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    padding-top: 0.5rem !important;
}
.sidebar-spacer {
    flex: 1 1 auto;
}

/* Shrink Streamlit's reserved header/collapse-button strip so the logo
   sits close to the actual top of the sidebar instead of leaving a gap. */
[data-testid="stSidebarHeader"] {
    min-height: 0;
    padding: 0.4rem 0.5rem 0 0.5rem;
}

/* Custom sidebar nav links (replaces st.page_link so we can use our own
   PNG icons instead of Streamlit's emoji/Material Symbols set).
   !important overrides Streamlit's own <a> styling (blue + underlined),
   which otherwise wins on specificity and leaks through. */
.sidebar-nav-link,
.sidebar-nav-link:link,
.sidebar-nav-link:visited {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    margin: 2px 0;
    border-radius: 8px;
    color: #94a3b8 !important;
    font-size: 0.88rem;
    font-weight: 500;
    text-decoration: none !important;
}
.sidebar-nav-link:hover {
    color: #e2e8f0 !important;
}
.sidebar-nav-link.active,
.sidebar-nav-link.active:link,
.sidebar-nav-link.active:visited {
    color: #ffffff !important;
    font-weight: 700;
}
.sidebar-nav-link img {
    opacity: 0.85;
}
.sidebar-nav-link.active img {
    opacity: 1;
}

/* Credit score readout box */
.credit-readout {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 9px 12px;
    font-size: 0.9rem;
}

/* Read-only field display in New Assessment - styled to look like the
   same bordered input boxes used in edit mode, just non-editable */
.field-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: #64748b;
    margin: 0 0 5px 0;
}
.field-box {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 0.9rem;
    color: #0f172a;
    background: #ffffff;
    margin: 0 0 14px 0;
}

/* Card section heading with a custom icon (New Assessment page) */
.card-heading {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 700;
    font-size: 0.95rem;
    color: #0f172a;
    margin-bottom: 14px;
}
</style>
"""


def inject_custom_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
