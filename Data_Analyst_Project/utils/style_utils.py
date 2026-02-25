import streamlit as st

def inject_bi_style():
    """Injects high-fidelity glassmorphic CSS for an executive PowerBI look."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f8fafc;
        }

        /* PowerBI-style Canvas */
        .main {
            background-color: transparent;
        }

        /* Glassmorphic Cards for Charts */
        div[data-testid="stVerticalBlock"] > div:has(div.stPlotlyChart) {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            margin-bottom: 30px;
        }

        /* Professional Metric Styling */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px 20px;
            border-radius: 12px;
            border-left: 5px solid #3b82f6;
        }
        
        div[data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-size: 0.9rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        div[data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-size: 2.1rem !important;
            font-weight: 700 !important;
        }

        /* Sidebar Glassmorphism */
        section[data-testid="stSidebar"] {
            background: rgba(15, 23, 42, 0.95) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Titles and Typography */
        h1, h2, h3 {
            color: #f1f5f9 !important;
            font-weight: 700 !important;
        }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0f172a;
        }
        ::-webkit-scrollbar-thumb {
            background: #334155;
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

def render_bi_header(title: str, subtitle: str):
    """Renders a professional header."""
    st.title(f"📊 {title}")
    st.markdown(f"**{subtitle}**")
    st.markdown("---")
