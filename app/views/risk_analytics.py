import streamlit as st
import math
import urllib.parse
from utils.data import RECENT_APPLICATIONS
from utils.components import render_html
from utils.icons import icon_img


def render():
    st.markdown("<h2 style='font-size: 1.5rem; font-weight: 700; margin: 0 0 4px 0; color: #0f172a;'>Risk Analysis</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85rem; color: #64748b; margin: 0 0 20px 0;'>Evaluate an applicant using AI-powered risk analysis.</p>", unsafe_allow_html=True)

    if "selected_applicant_name" not in st.session_state:
        st.session_state["selected_applicant_name"] = RECENT_APPLICATIONS[0]["applicant"]

    selected_name = st.session_state["selected_applicant_name"]

    applicant = next(
        (app for app in RECENT_APPLICATIONS if app["applicant"] == selected_name),
        RECENT_APPLICATIONS[0],
    )

    score = applicant.get("risk_score", 18)
    level = applicant.get("risk_level", "low")

    # Styling mapping
    level_colors = {
        "low": {"text": "#059669", "bg": "#d1fae5", "label": "LOW RISK"},
        "medium": {"text": "#f59e0b", "bg": "#fef3c7", "label": "MEDIUM RISK"},
        "high": {"text": "#dc2626", "bg": "#fee2e2", "label": "HIGH RISK"},
    }
    color_info = level_colors.get(level, level_colors["low"])
    score_color = color_info["text"]
    badge_bg = color_info["bg"]
    badge_label = color_info["label"]
    rec_text = "APPROVE" if level == "low" else ("REVIEW" if level == "medium" else "REJECT")
    rec_color = score_color

# SVG gauge geometry matching the reference
    cx, cy = 180, 160
    r_needle = 85
    angle = 180 + (score * 1.8)
    rad = math.radians(angle)
    
    # Calculate pointed needle polygon coordinates
    nx = cx + r_needle * math.cos(rad)
    ny = cy + r_needle * math.sin(rad)
    base_w = 4
    rad_p1 = rad + math.pi/2
    rad_p2 = rad - math.pi/2
    px1 = cx + base_w * math.cos(rad_p1)
    py1 = cy + base_w * math.sin(rad_p1)
    px2 = cx + base_w * math.cos(rad_p2)
    py2 = cy + base_w * math.sin(rad_p2)

    gauge_svg = (
        f'<svg viewBox="0 0 360 220" width="100%" height="auto" style="display:block;max-width:340px;margin:0 auto;overflow:visible;">'
        # Colored Donut Segments (Inner R: 76, Outer R: 114)
        f'<path d="M 66 160 A 114 114 0 0 1 112.2 68.4 L 134.8 98.9 A 76 76 0 0 0 104 160 Z" fill="#00a854"/>'
        f'<path d="M 113.8 67.2 A 114 114 0 0 1 214.3 51.3 L 202.8 87.5 A 76 76 0 0 0 135.9 98.1 Z" fill="#ff9900"/>'
        f'<path d="M 216.2 51.9 A 114 114 0 0 1 294 160 L 256 160 A 76 76 0 0 0 204.1 87.9 Z" fill="#e31a22"/>'
        # Sector Labels (Above arc) - ADJUSTED LOW & HIGH POSITIONS
        f'<text x="75" y="60" fill="#006837" font-size="12" font-weight="700" text-anchor="middle" font-family="sans-serif">LOW</text>'
        f'<text x="180" y="30" fill="#ff9900" font-size="12" font-weight="700" text-anchor="middle" font-family="sans-serif">MEDIUM</text>'
        f'<text x="285" y="60" fill="#e31a22" font-size="12" font-weight="700" text-anchor="middle" font-family="sans-serif">HIGH</text>'
        # Scale Ticks (Inside inner arc perimeter)
        f'<text x="120" y="156" fill="#1e293b" font-size="10" font-weight="700" text-anchor="middle" font-family="sans-serif">0%</text>'
        f'<text x="146" y="106" fill="#1e293b" font-size="10" font-weight="700" text-anchor="middle" font-family="sans-serif">30%</text>'
        f'<text x="214" y="106" fill="#1e293b" font-size="10" font-weight="700" text-anchor="middle" font-family="sans-serif">60%</text>'
        f'<text x="240" y="156" fill="#1e293b" font-size="10" font-weight="700" text-anchor="middle" font-family="sans-serif">100%</text>'
        # Needle & Pivot Cap
        f'<polygon points="{nx:.1f},{ny:.1f} {px1:.1f},{py1:.1f} {px2:.1f},{py2:.1f}" fill="#0f172a"/>'
        f'<circle cx="{cx}" cy="{cy}" r="8" fill="#0f172a"/>'
        # Bottom Readout
        f'<text x="180" y="196" fill="#00a854" font-size="28" font-weight="800" text-anchor="middle" font-family="sans-serif">{score}%</text>'
        f'<text x="180" y="214" fill="#334155" font-size="10.5" font-weight="700" letter-spacing="0.08em" text-anchor="middle" font-family="sans-serif">RICK SCORE</text>'
        f'</svg>'
    )
    
    risk_card_html = f"""
    <div style="background: #ffffff; border-radius: 16px; padding: 36px 40px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); display: flex; align-items: center; justify-content: space-between; gap: 30px; margin-bottom: 24px;">
        <div style="flex: 1; min-width: 200px;">
            <div style="font-size: 3.2rem; font-weight: 800; color: {score_color}; line-height: 1;">{score}%</div>
            <div style="margin-top: 12px; display: inline-flex; align-items: center; gap: 6px; background: {badge_bg}; color: {score_color}; padding: 4px 12px; border-radius: 999px; font-size: 0.78rem; font-weight: 700;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="{score_color}" stroke="none"><circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
                {badge_label}
            </div>
            <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0 16px 0; width: 100%; max-width: 280px;" />
            <div style="font-size: 0.7rem; font-weight: 600; color: #64748b; text-transform: uppercase; background: #f1f5f9; padding: 4px 8px; border-radius: 6px; display: inline-block; margin-bottom: 6px;">RECOMMENDATION</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: {rec_color}; line-height: 1;">{rec_text}</div>
        </div>
        <div style="flex: 1.2; display: flex; justify-content: center; align-items: center;">
            {gauge_svg}
        </div>
    </div>
    """
    render_html(risk_card_html)

    # Bottom Row: Model Performance on the left, Navigation Buttons on the right
    col1, col2 = st.columns([1, 1.2])

    with col1:
        model_perf_html = f"""
        <div style="background: #ffffff; border-radius: 16px; padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.06);">
            <div style="font-size: 1rem; font-weight: 700; color: #0f172a; margin-bottom: 16px;">Model Performance</div>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <div style="display: flex; align-items: center; justify-content: space-between; background: #f8fafc; border-radius: 8px; padding: 10px 14px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="display: flex; align-items: center; justify-content: center; width: 22px; height: 22px;">
                            {icon_img("accuracy", size=18, alt="Accuracy")}
                        </div>
                        <span style="font-size: 0.88rem; color: #475569; font-weight: 500;">Accuracy</span>
                    </div>
                    <span style="font-size: 0.92rem; font-weight: 700; color: #2563eb;">0.82</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; background: #f8fafc; border-radius: 8px; padding: 10px 14px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="display: flex; align-items: center; justify-content: center; width: 22px; height: 22px;">
                            {icon_img("precision", size=18, alt="Precision")}
                        </div>
                        <span style="font-size: 0.88rem; color: #475569; font-weight: 500;">Precision</span>
                    </div>
                    <span style="font-size: 0.92rem; font-weight: 700; color: #2563eb;">0.84</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; background: #f8fafc; border-radius: 8px; padding: 10px 14px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="display: flex; align-items: center; justify-content: center; width: 22px; height: 22px;">
                            {icon_img("recall", size=18, alt="Recall")}
                        </div>
                        <span style="font-size: 0.88rem; color: #475569; font-weight: 500;">Recall</span>
                    </div>
                    <span style="font-size: 0.92rem; font-weight: 700; color: #2563eb;">0.81</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; background: #f8fafc; border-radius: 8px; padding: 10px 14px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="display: flex; align-items: center; justify-content: center; width: 22px; height: 22px;">
                            {icon_img("ROC", size=18, alt="ROC-AUC")}
                        </div>
                        <span style="font-size: 0.88rem; color: #475569; font-weight: 500;">ROC-AUC</span>
                    </div>
                    <span style="font-size: 0.92rem; font-weight: 700; color: #2563eb;">0.88</span>
                </div>
            </div>
        </div>
        """
        render_html(model_perf_html)

    with col2:
        encoded_name = urllib.parse.quote(selected_name)
        buttons_html = f"""
        <div style="display: flex; justify-content: flex-end; align-items: flex-end; height: 100%; gap: 12px; padding-bottom: 8px;">
            <a href="new-assessment?applicant={encoded_name}" target="_self" class="btn-outline">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                View Applicant Profile
            </a>
            <a href="decision-explanation?applicant={encoded_name}" target="_self" class="btn-filled">
                View Decision Explaination
            </a>
        </div>
        """
        render_html(buttons_html)