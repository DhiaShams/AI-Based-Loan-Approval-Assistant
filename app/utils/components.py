import streamlit as st
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


def applications_table(applications):
    rows = "".join(f"""
        <tr>
            <td class="applicant">{app['applicant']}</td>
            <td>{format_currency(app['amount'])}</td>
            <td>{app['risk_score']}%</td>
            <td>{risk_badge_html(app['risk_level'])}</td>
            <td>{decision_html(app['decision'])}</td>
        </tr>
    """ for app in applications)

    render_html(f"""
        <div class="loanai-card">
            <div class="loanai-table-header">
                <p class="loanai-table-title">Recent Applications</p>
                <a class="loanai-view-all" href="#">View All &rsaquo;</a>
            </div>
            <div class="loanai-table-scroll">
                <table class="loanai-table">
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
    """Custom nav link (replaces st.page_link) so we can show a custom
    PNG icon next to each item - st.Page's built-in `icon` only supports
    emoji/Material Symbols, not arbitrary images."""
    href = page.url_path or "/"
    render_html(f"""
        <a href="{href}" target="_self" class="sidebar-nav-link{' active' if active else ''}">
            {icon_img(icon_name, size=18, alt=page.title)}
            <span>{page.title}</span>
        </a>
    """)


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
