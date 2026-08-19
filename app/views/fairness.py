import streamlit as st
from utils.components import render_html
from utils.icons import icon_img


def render(dashboard_page):
    # Top Header Row (Title & Subtitle on Left, Fairness Status Card on Right)
    col_title, col_status = st.columns([2.2, 1.2])

    with col_title:
        st.markdown(
            "<h2 style='font-size: 1.6rem; font-weight: 700; margin: 0 0 4px 0; color: #0f172a;'>Fairness Analysis</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='font-size: 0.84rem; color: #64748b; margin: 0; line-height: 1.4;'>We ensure fairness across demographic groups and promote responsible use of AI in lending decisions.</p>",
            unsafe_allow_html=True,
        )

    with col_status:
        status_card_html = """
        <div style="background: #ffffff; border-radius: 12px; padding: 14px 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #f1f5f9; display: flex; align-items: center; gap: 14px;">
            <div style="background: #eff6ff; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
            </div>
            <div>
                <div style="font-size: 0.85rem; font-weight: 700; color: #0f172a; margin-bottom: 4px;">Fairness Status</div>
                <div style="display: inline-block; background: #dcfce7; color: #16a34a; font-size: 0.75rem; font-weight: 700; padding: 2px 14px; border-radius: 999px; margin-bottom: 4px;">
                    FAIR
                </div>
                <div style="font-size: 0.65rem; color: #94a3b8;">No significant disparities detected</div>
            </div>
        </div>
        """
        render_html(status_card_html)

    st.write("")

    # Group Comparison Table Container
    comparison_card_html = f"""
    <div style="background: #ffffff; border-radius: 16px; padding: 28px 32px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; margin-bottom: 28px;">
        <h3 style="font-size: 1.1rem; font-weight: 700; color: #0f172a; margin: 0 0 18px 0;">Group Comparison</h3>
        
        <div style="background: #f8fafc; border-radius: 12px; padding: 20px 24px; border: 1px solid #e2e8f0; box-shadow: inset 0 1px 3px rgba(0,0,0,0.02);">
            <table style="width: 100%; border-collapse: collapse; text-align: center;">
                <thead>
                    <tr style="border-bottom: 1px solid #cbd5e1;">
                        <th style="text-align: left; padding: 12px 16px; font-size: 0.95rem; font-weight: 700; color: #0f172a; width: 34%;">Metric</th>
                        <th style="padding: 12px 16px; font-size: 0.95rem; font-weight: 700; color: #0f172a; width: 33%; border-left: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0;">
                            Group A<br>
                            <span style="font-size: 0.72rem; font-weight: 500; color: #64748b;">(Reference Group)</span>
                        </th>
                        <th style="padding: 12px 16px; font-size: 0.95rem; font-weight: 700; color: #0f172a; width: 33%;">
                            Group B<br>
                            <span style="font-size: 0.72rem; font-weight: 500; color: #64748b;">(Comparison Group)</span>
                        </th>
                    </tr>
                </thead>
                <tbody style="background: #ffffff;">
                    <!-- Precision -->
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="text-align: left; padding: 16px 20px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                {icon_img("precision", size=18, alt="Precision")}
                                <span style="font-size: 0.88rem; font-weight: 600; color: #334155;">Precision</span>
                            </div>
                        </td>
                        <td style="padding: 16px; font-size: 1.05rem; font-weight: 700; color: #2563eb; border-left: 1px solid #f1f5f9; border-right: 1px solid #f1f5f9;">0.84</td>
                        <td style="padding: 16px; font-size: 1.05rem; font-weight: 700; color: #2563eb;">0.81</td>
                    </tr>
                    
                    <!-- Recall -->
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="text-align: left; padding: 16px 20px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>
                                </svg>
                                <span style="font-size: 0.88rem; font-weight: 600; color: #334155;">Recall</span>
                            </div>
                        </td>
                        <td style="padding: 16px; font-size: 1.05rem; font-weight: 700; color: #2563eb; border-left: 1px solid #f1f5f9; border-right: 1px solid #f1f5f9;">0.82</td>
                        <td style="padding: 16px; font-size: 1.05rem; font-weight: 700; color: #2563eb;">0.79</td>
                    </tr>
                    
                    <!-- FPR -->
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="text-align: left; padding: 14px 20px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                                </svg>
                                <div>
                                    <div style="font-size: 0.88rem; font-weight: 600; color: #334155;">FPR</div>
                                    <div style="font-size: 0.72rem; color: #64748b;">(False Positive Rate)</div>
                                </div>
                            </div>
                        </td>
                        <td style="padding: 14px; font-size: 1.05rem; font-weight: 700; color: #2563eb; border-left: 1px solid #f1f5f9; border-right: 1px solid #f1f5f9;">0.11</td>
                        <td style="padding: 14px; font-size: 1.05rem; font-weight: 700; color: #2563eb;">0.14</td>
                    </tr>
                    
                    <!-- FNR -->
                    <tr>
                        <td style="text-align: left; padding: 14px 20px;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                                    <line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/>
                                </svg>
                                <div>
                                    <div style="font-size: 0.88rem; font-weight: 600; color: #334155;">FNR</div>
                                    <div style="font-size: 0.72rem; color: #64748b;">(False Negative Rate)</div>
                                </div>
                            </div>
                        </td>
                        <td style="padding: 14px; font-size: 1.05rem; font-weight: 700; color: #2563eb; border-left: 1px solid #f1f5f9; border-right: 1px solid #f1f5f9;">0.18</td>
                        <td style="padding: 14px; font-size: 1.05rem; font-weight: 700; color: #2563eb;">0.21</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    """
    render_html(comparison_card_html)

    st.markdown(
        """
        <style>
        .st-key-back-dashboard button {
            border: 1px solid #2563eb;
            border-radius: 8px;
            color: #2563eb;
            background: #ffffff;
            font-size: 0.85rem;
            font-weight: 600;
            padding: 8px 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.container(key="back-dashboard"):
        if st.button(
            "Back to Dashboard",
            icon=":material/arrow_back:",
            key="back_dashboard_button",
        ):
            st.switch_page(dashboard_page)