import streamlit as st
import urllib.parse
from utils.data import RECENT_APPLICATIONS
from utils.components import render_html


def _render_segmented_bar(value_score, is_increase_risk, total_blocks=10):
    """Renders a 10-block segmented bar chart matching the reference UI."""
    active_blocks = min(total_blocks, max(1, int(round((abs(value_score) / 0.15) * total_blocks))))
    
    if is_increase_risk:
        active_style = "background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%);"
    else:
        active_style = "background: linear-gradient(180deg, #10b981 0%, #059669 100%);"
        
    inactive_style = "background: linear-gradient(180deg, #e2e8f0 0%, #cbd5e1 100%);"

    blocks_html = []
    for i in range(total_blocks):
        style = active_style if i < active_blocks else inactive_style
        blocks_html.append(
            f'<div style="flex: 1; height: 18px; {style} border-radius: 2px;"></div>'
        )

    return f'<div style="display: flex; gap: 3px; width: 100%; max-width: 280px;">{"".join(blocks_html)}</div>'


def render():
    st.markdown("<h2 style='font-size: 1.6rem; font-weight: 700; margin: 0 0 4px 0; color: #0f172a;'>Decision Explanation</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85rem; color: #64748b; margin: 0 0 24px 0;'>Why did the AI make this decision?</p>", unsafe_allow_html=True)

    if "selected_applicant_name" not in st.session_state:
        st.session_state["selected_applicant_name"] = RECENT_APPLICATIONS[0]["applicant"]

    selected_name = st.session_state["selected_applicant_name"]
    encoded_name = urllib.parse.quote(selected_name)

    # SHAP Drivers Card
    shap_card_html = f"""
    <div style="background: #ffffff; border-radius: 16px; padding: 28px 36px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #f1f5f9; margin-bottom: 28px;">
        <h3 style="font-size: 1.2rem; font-weight: 700; color: #0f172a; margin: 0 0 20px 0;">SHAP Drivers</h3>
        
        <!-- Factors Increasing Risk -->
        <p style="font-size: 0.82rem; font-weight: 700; color: #ef4444; margin: 0 0 16px 0;">Factors increasing risk</p>
        
        <div style="display: flex; flex-direction: column;">
            <!-- Debt-to-Income ratio -->
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px; padding-bottom: 14px;">
                <div style="width: 200px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #1e293b;">Debt-to-Income ratio</div>
                    <div style="font-size: 0.75rem; color: #64748b;">15%</div>
                </div>
                {_render_segmented_bar(0.07, is_increase_risk=True)}
                <div style="width: 60px; text-anchor: end; text-align: right; font-size: 0.88rem; font-weight: 700; color: #ef4444;">+0.07</div>
            </div>
            
            <div style="border-bottom: 1px solid #e2e8f0; margin-bottom: 14px;"></div>

            <!-- Loan Amount -->
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px; padding-bottom: 14px;">
                <div style="width: 200px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #1e293b;">Loan Amount</div>
                    <div style="font-size: 0.75rem; color: #64748b;">₹5,00,000</div>
                </div>
                {_render_segmented_bar(0.04, is_increase_risk=True)}
                <div style="width: 60px; text-anchor: end; text-align: right; font-size: 0.88rem; font-weight: 700; color: #ef4444;">+0.04</div>
            </div>

            <div style="border-bottom: 1px solid #e2e8f0; margin-bottom: 20px;"></div>

            <!-- Factors Decreasing Risk -->
            <p style="font-size: 0.82rem; font-weight: 700; color: #10b981; margin: 0 0 16px 0;">Factors decreasing risk</p>

            <!-- Credit Score -->
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px; padding-bottom: 14px;">
                <div style="width: 200px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #1e293b;">Credit Score</div>
                    <div style="font-size: 0.75rem; color: #64748b;">720 (Excellent)</div>
                </div>
                {_render_segmented_bar(0.12, is_increase_risk=False)}
                <div style="width: 60px; text-anchor: end; text-align: right; font-size: 0.88rem; font-weight: 700; color: #10b981;">-0.12</div>
            </div>

            <div style="border-bottom: 1px solid #e2e8f0; margin-bottom: 14px;"></div>

            <!-- Income -->
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px; padding-bottom: 14px;">
                <div style="width: 200px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #1e293b;">Income</div>
                    <div style="font-size: 0.75rem; color: #64748b;">₹60,000/year</div>
                </div>
                {_render_segmented_bar(0.08, is_increase_risk=False)}
                <div style="width: 60px; text-anchor: end; text-align: right; font-size: 0.88rem; font-weight: 700; color: #10b981;">-0.08</div>
            </div>

            <div style="border-bottom: 1px solid #e2e8f0; margin-bottom: 14px;"></div>

            <!-- Employment Length -->
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px;">
                <div style="width: 200px;">
                    <div style="font-size: 0.88rem; font-weight: 700; color: #1e293b;">Employment Length</div>
                    <div style="font-size: 0.75rem; color: #64748b;">5 Years</div>
                </div>
                {_render_segmented_bar(0.05, is_increase_risk=False)}
                <div style="width: 60px; text-anchor: end; text-align: right; font-size: 0.88rem; font-weight: 700; color: #10b981;">-0.05</div>
            </div>

            <!-- Axis Scale Line -->
            <div style="display: flex; justify-content: center; margin-top: 18px;">
                <div style="width: 100%; max-width: 380px; display: flex; flex-direction: column; align-items: center;">
                    <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; font-size: 0.72rem; color: #64748b;">
                        <span>&larr; -0.15</span>
                        <span>0 (No Impact)</span>
                        <span>+0.15 &rarr;</span>
                    </div>
                    <div style="height: 1px; background: #cbd5e1; width: 100%; margin-top: 2px;"></div>
                </div>
            </div>
        </div>
    </div>
    """
    render_html(shap_card_html)

    # AI Explanation Section
    ai_card_html = """
    <div style="margin-bottom: 28px;">
        <h3 style="font-size: 1.2rem; font-weight: 700; color: #0f172a; margin: 0 0 12px 0;">AI Explanation</h3>
        <div style="background: #ffffff; border-radius: 12px; padding: 22px 28px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #f1f5f9;">
            <p style="font-size: 0.9rem; color: #334155; line-height: 1.6; margin: 0;">
                The applicant's strong credit score and stable employment significantly reduce the predicted risk. However, the requested loan amount and existing debt-to-income ratio increase the risk slightly.
            </p>
        </div>
    </div>
    """
    render_html(ai_card_html)

    # Bottom Actions
    buttons_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">
        <a href="risk-analytics?applicant={encoded_name}" target="_self" style="text-decoration: none; display: inline-flex; align-items: center; border: 1.5px solid #3b82f6; color: #2563eb; background: #ffffff; border-radius: 8px; font-size: 0.85rem; font-weight: 600; padding: 10px 18px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
            Back to Risk Analysis
        </a>
        <a href="new-assessment?applicant={encoded_name}" target="_self" style="text-decoration: none; display: inline-flex; align-items: center; background: #1d4ed8; color: #ffffff; border-radius: 8px; font-size: 0.85rem; font-weight: 600; padding: 10px 20px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            View Applicant Profile
        </a>
    </div>
    """
    render_html(buttons_html)