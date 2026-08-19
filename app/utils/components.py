import streamlit as st
import urllib.parse
from utils.format import format_currency, risk_level_label, decision_label
from utils.icons import icon_img


def render_html(html):
    """Render raw HTML via st.markdown. Strips per-line indentation first,
    since Streamlit's markdown parser treats 4+ leading spaces as a code
    block, which otherwise causes fragments of the HTML to render as a
    visible code snippet instead of actual markup."""
    cleaned = "\n".join(line.strip() for line in html.strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def stat_card(label, value):
    render_html(f"""
        <div class="loanai-card">
            <p class="loanai-card-label">{label}</p>
            <p class="loanai-card-value">{value}</p>
        </div>
    """)


def risk_badge_html(level):
    return f'<span class="badge badge-{level}">{risk_level_label(level)}</span>'


def decision_html(decision):
    return f'<span class="decision decision-{decision}">{decision_label(decision).upper()}</span>'


def applications_table(applications, show_search=False, show_view_all=False):
    rows = "".join(f"""
        <tr>
            <td class="applicant">
                <a href="new-assessment?applicant={urllib.parse.quote(app['applicant'])}" target="_self" class="applicant-link">{app['applicant']}</a>
            </td>
            <td>{format_currency(app['amount'])}</td>
            <td>{app['risk_score']}%</td>
            <td>{risk_badge_html(app['risk_level'])}</td>
            <td>{decision_html(app['decision'])}</td>
        </tr>
    """ for app in applications)

    # Build the header right-side elements based on settings
    header_right = ""
    if show_search:
        header_right = """
            <div class="loanai-search-container">
                <svg class="loanai-search-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
                <input type="text" id="loanai-search-input" class="loanai-search-input" onkeyup="filterApplications()" placeholder="Search" autocomplete="off">
            </div>
        """
    elif show_view_all:
        header_right = '<a class="loanai-view-all" href="applications?search=1" target="_self">View All &rsaquo;</a>'

    # Client-side filtering script to avoid slow Streamlit reruns
    search_script = ""
    if show_search:
        search_script = """
            <script>
            if (typeof window.filterApplications === 'undefined') {
                window.filterApplications = function() {
                    var input = document.getElementById("loanai-search-input");
                    if (!input) return;
                    var filter = input.value.toLowerCase();
                    var table = document.getElementById("loanai-applications-table");
                    if (!table) return;
                    var tr = table.getElementsByTagName("tr");

                    for (var i = 1; i < tr.length; i++) {
                        var row = tr[i];
                        var textContent = row.textContent || row.innerText;
                        if (textContent.toLowerCase().indexOf(filter) > -1) {
                            row.style.display = "";
                        } else {
                            row.style.display = "none";
                        }
                    }
                };
            }
            // Trigger initial filtering if input was pre-populated (e.g. browser cache)
            setTimeout(function() {
                if (window.filterApplications) window.filterApplications();
            }, 100);
            </script>
        """

    render_html(f"""
        <div class="loanai-card">
            <div class="loanai-table-header">
                <p class="loanai-table-title">Recent Applications</p>
                {header_right}
            </div>
            <div class="loanai-table-scroll">
                <table class="loanai-table" id="loanai-applications-table">
                    <thead>
                        <tr>
                            <th>Applicant</th>
                            <th>Amount</th>
                            <th>Risk Score</th>
                            <th>Risk Level</th>
                            <th>Decision</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>
        {search_script}
    """)


def sidebar_brand():
    render_html(f"""
        <div class="sidebar-brand">
            {icon_img('loan_ai', size=34, alt='Loan AI', css_class='sidebar-brand-icon')}
            <div>
                <p class="sidebar-brand-title">LOAN AI</p>
                <p class="sidebar-brand-subtitle">DECISION INTELLIGENCE</p>
            </div>
        </div>
    """)


def sidebar_nav_link(page, icon_name, active=False):
    """Use Streamlit's native router to avoid a full document reload."""
    material_icons = {
        "dashboard": ":material/dashboard:",
        "new_assessment": ":material/note_add:",
        "applications": ":material/description:",
        "risk_analysis": ":material/analytics:",
        "decision_explanation": ":material/chat:",
        "fairness": ":material/balance:",
        "settings": ":material/settings:",
    }
    st.page_link(page, label=page.title, icon=material_icons.get(icon_name))


def sidebar_user_footer(user):
    render_html(f"""
        <div class="sidebar-user">
            {icon_img('profile-avatar', size=34, alt=user['name'], css_class='sidebar-avatar')}
            <div>
                <p class="sidebar-user-name">{user['name']}</p>
                <p class="sidebar-user-role">{user['role']}</p>
            </div>
        </div>
    """)


def sidebar_spacer():
    render_html('<div class="sidebar-spacer"></div>')


def card_heading(icon_name, text):
    """Card section heading with a custom icon (replaces the emoji +
    bold-markdown headings previously used on the New Assessment page)."""
    render_html(f"""
        <div class="card-heading">
            {icon_img(icon_name, size=18, alt=text)}
            <span>{text}</span>
        </div>
    """)
