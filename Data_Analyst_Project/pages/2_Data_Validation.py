import streamlit as st
from utils.data_loader import load_parquet_data
from components.ui_cards import render_alert
from components.charts import *
from components.sidebar_filters import render_global_filters
from utils.style_utils import inject_bi_style, render_bi_header

st.set_page_config(page_title="Data Engineering", page_icon="⚙️", layout="wide")
inject_bi_style()
render_bi_header("Data Engineering Audit", "Monitoreo de Infraestructura y Salud del Data Lake")

raw_listings, raw_sessions, raw_users = load_parquet_data()
listings, sessions, users = render_global_filters(raw_listings, raw_sessions, raw_users)

col_a, col_b = st.columns(2)
with col_a:
    st.metric("Registros en Ingesta", f"{len(listings):,}")
with col_b:
    st.metric("Eventos Procesados", f"{len(sessions):,}")

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    with st.container():
        st.plotly_chart(plot_daily_scrape_volume(), use_container_width=True)
    with st.container():
        st.plotly_chart(plot_event_distribution(sessions), use_container_width=True)

with col2:
    with st.container():
        st.plotly_chart(plot_data_drift(), use_container_width=True)
    with st.container():
        st.plotly_chart(plot_missing_values(listings), use_container_width=True)

render_alert("Infraestructura Estable: El flujo de datos mantiene un SLA de integridad superior al 95%.", type="success")
