import streamlit as st

def inject_bi_style():
    """Injects ultra-premium 'Deep Glass' CSS for a full executive experience."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700&display=swap');
        
        /* Immersive Mode: Hide Streamlit standard elements */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f3f2f1; /* Power BI classic light grey */
            color: #323130; /* Power BI classic dark grey */
        }

        /* PowerBI-style Canvas */
        .main {
            background-color: transparent;
            padding-top: 0rem !important;
        }

        /* PowerBI Solid White Cards */
        div[data-testid="stVerticalBlock"] > div:has(div.stPlotlyChart) {
            background: #ffffff;
            border: 1px solid #e1dfdd;
            border-radius: 4px;
            padding: 20px;
            box-shadow: 0 1.6px 3.6px 0 rgba(0,0,0,.132), 0 0.3px 0.9px 0 rgba(0,0,0,.108);
            margin-bottom: 25px;
            transition: box-shadow 0.2s ease;
        }
        
        div[data-testid="stVerticalBlock"] > div:has(div.stPlotlyChart):hover {
            box-shadow: 0 6.4px 14.4px 0 rgba(0,0,0,.132), 0 1.2px 3.6px 0 rgba(0,0,0,.108);
        }

        /* PowerBI Solid Metrics */
        div[data-testid="stMetric"] {
            background: #ffffff;
            padding: 15px 20px;
            border-radius: 4px;
            border: 1px solid #e1dfdd;
            border-left: 4px solid #118DFF; /* Power BI Blue Accent */
            box-shadow: 0 1.6px 3.6px 0 rgba(0,0,0,.132), 0 0.3px 0.9px 0 rgba(0,0,0,.108);
        }
        
        div[data-testid="stMetricLabel"] {
            color: #605e5c !important; /* Secondary grey */
            font-size: 0.90rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        div[data-testid="stMetricValue"] {
            color: #323130 !important;
            font-size: 2.1rem !important;
            font-weight: 700 !important;
            font-family: 'Segoe UI', sans-serif;
        }

        /* Immersive Sidebar - Dark */
        section[data-testid="stSidebar"] {
            background: #252423 !important; /* Authentic dark grey sidebar */
            border-right: 1px solid #323130;
            color: #ffffff !important;
        }
        
        /* Force Sidebar Text to be White */
        [data-testid="stSidebarNav"] span, 
        [data-testid="stSidebarNav"] a, 
        .st-emotion-cache-16txtl3 p {
            color: #ffffff !important;
            font-weight: 400 !important;
        }

        /* Segmentadores (Slicers) Power BI Theme (Light inside main body) */
        div.stSelectbox > label, div.stSlider > label {
            color: #323130 !important; 
            font-weight: 600 !important;
            font-size: 0.95rem !important;
        }
        /* Slicers in sidebar need white labels */
        section[data-testid="stSidebar"] div.stSelectbox > label, 
        section[data-testid="stSidebar"] div.stSlider > label {
            color: #ffffff !important; 
        }

        div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #323130 !important;
            border: 1px solid #8a8886 !important;
            border-radius: 2px !important;
            box-shadow: none !important;
        }
        div[data-baseweb="popover"] ul {
            background-color: #ffffff !important;
            color: #323130 !important;
            border: 1px solid #e1dfdd !important;
        }

        /* Smooth Page Transitions */
        .stApp {
            animation: fadeIn 0.4s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #f3f2f1; }
        ::-webkit-scrollbar-thumb { background: #c8c6c4; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

def render_bi_header(title: str, subtitle: str):
    """Renders a professional header."""
    st.title(f"📊 {title}")
    st.markdown(f"**{subtitle}**")
    st.markdown("---")
