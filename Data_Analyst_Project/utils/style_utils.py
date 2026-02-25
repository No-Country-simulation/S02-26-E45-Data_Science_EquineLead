import streamlit as st

def inject_bi_style():
    """Injects ultra-premium 'Deep Glass' CSS for a full executive experience."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        /* Immersive Mode: Hide Streamlit standard elements */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            background: radial-gradient(circle at top left, #1e293b 0%, #0f172a 100%);
            color: #f8fafc;
        }

        /* PowerBI-style Canvas */
        .main {
            background-color: transparent;
            padding-top: 0rem !important;
        }

        /* Ultra-Premium Glass Cards */
        div[data-testid="stVerticalBlock"] > div:has(div.stPlotlyChart) {
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(12px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            margin-bottom: 35px;
            transition: transform 0.3s ease, border-color 0.3s ease;
        }
        
        div[data-testid="stVerticalBlock"] > div:has(div.stPlotlyChart):hover {
            border-color: rgba(59, 130, 246, 0.4);
            transform: translateY(-5px);
        }

        /* Metrics with Glass & Glow */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(5px);
            padding: 20px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-left: 6px solid #3b82f6;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        div[data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }

        div[data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-size: 2.3rem !important;
            font-weight: 800 !important;
        }

        /* Immersive Sidebar */
        section[data-testid="stSidebar"] {
            background: rgba(15, 23, 42, 0.98) !important;
            border-right: 1px solid rgba(59, 130, 246, 0.2);
            box-shadow: 10px 0 30px -15px rgba(0, 0, 0, 0.5);
        }
        [data-testid="stSidebarNav"] span {
            color: #f8fafc !important;
            font-weight: 600;
        }

        /* Segmentadores (Slicers) Dark Theme */
        div.stSelectbox > label {
            color: #94a3b8 !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px;
        }
        div[data-baseweb="select"] > div {
            background-color: rgba(30, 41, 59, 0.8) !important;
            color: #ffffff !important;
            border: 1px solid rgba(59, 130, 246, 0.3) !important;
            border-radius: 8px !important;
        }
        div[data-baseweb="popover"] ul {
            background-color: #0f172a !important;
            color: #ffffff !important;
        }

        /* Smooth Page Transitions */
        .stApp {
            animation: fadeIn 0.8s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.98); }
            to { opacity: 1; transform: scale(1); }
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

def render_bi_header(title: str, subtitle: str):
    """Renders a professional header."""
    st.title(f"📊 {title}")
    st.markdown(f"**{subtitle}**")
    st.markdown("---")
