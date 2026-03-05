import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from utils.style_utils import inject_premium_style
from utils.data_loader import get_all_dashboard_data
from modules.executive_summary import render_executive_summary
from modules.horse_analytics import render_horse_analytics
from modules.retail_analytics import render_retail_analytics
from modules.audience_analytics import render_audience_analytics
from modules.conversion_analytics import render_conversion_analytics
from modules.ai_subsystem import render_ai_subsystem
import subprocess
import os

@st.cache_resource
@st.cache_resource
def pull_data():
    import json
    import tempfile

    creds = st.secrets["gcp"]["credentials"]
    
    # Streamlit puede devolvelo como dict o string
    if isinstance(creds, str):
        creds_dict = json.loads(creds.strip())
    else:
        creds_dict = dict(creds)

    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(creds_dict, tmp)
    tmp.flush()
    tmp.close()

    # Borrar lock si existe
    lock_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".dvc", "tmp", "lock"))
    if os.path.exists(lock_path):
        os.remove(lock_path)

    result = subprocess.run(
        ["dvc", "pull", "--remote", "gcsremote"],
        capture_output=True,
        text=True,
        env={**os.environ, "GOOGLE_APPLICATION_CREDENTIALS": tmp.name}
    )
    if result.returncode != 0:
        st.error(f"DVC pull failed:\n{result.stderr}")
    else:
        st.success("Data pulled OK")

pull_data()

# ---------------------------------------------
# 1. GLOBAL CONFIGURATION & AESTHETICS
# ---------------------------------------------
st.set_page_config(
    page_title="EquineLead Analytics PRO", 
    layout="wide", 
    page_icon="📈", 
    initial_sidebar_state="expanded"
)

# Inject Premium Dark Theme
inject_premium_style()

# ---------------------------------------------
# 2. GLOBAL DATA SYNCHRONIZATION
# ---------------------------------------------
df_horses, df_products, df_users, df_u_sessions, df_p_sessions = get_all_dashboard_data()

# ---------------------------------------------
# 3. SIDEBAR NAVIGATION
# ---------------------------------------------
st.sidebar.markdown("<h2 style='text-align: center; color: #00B8D9; font-weight: 800;'>EQUINELEAD PRO</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 0.9em; color: #64748B;'>Executive Analytics Engine</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

page = st.sidebar.radio("REPORT VIEWS", [
    "📊 1. Executive Summary",
    "🐎 2. Horse Inventory Metrics",
    "📦 3. Ecommerce & Products",
    "🌍 4. Global Audience",
    "⚡ 5. Conversion & Funnels",
    "🧠 6. AI Subsystem (Dagshub)"
])

st.sidebar.markdown("---")
st.sidebar.caption("System Status: **ONLINE**")
st.sidebar.caption("Latency: **Optimized**")
st.sidebar.caption("Architecture: **Modularized**")

# ---------------------------------------------
# 4. ROUTING & RENDERING
# ---------------------------------------------
if page == "📊 1. Executive Summary":
    render_executive_summary(df_users, df_horses, df_products, df_u_sessions, df_p_sessions)

elif page == "🐎 2. Horse Inventory Metrics":
    render_horse_analytics(df_horses)

elif page == "📦 3. Ecommerce & Products":
    render_retail_analytics(df_products)

elif page == "🌍 4. Global Audience":
    render_audience_analytics(df_users)

elif page == "⚡ 5. Conversion & Funnels":
    render_conversion_analytics(df_u_sessions, df_p_sessions)

elif page == "🧠 6. AI Subsystem (Dagshub)":
    render_ai_subsystem()

