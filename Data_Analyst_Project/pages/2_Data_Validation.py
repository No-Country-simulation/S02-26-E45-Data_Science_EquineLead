import streamlit as st
from utils.data_loader import load_parquet_data
from components.ui_cards import render_kpi_card, render_alert
from components.charts import *

st.set_page_config(page_title="Data Engineering (Infra)", page_icon="⚙️", layout="wide")

st.header("2. Auditoría Operativa del Data Lake")
st.markdown("Monitoreo en tiempo real de la Extracción Cruda, Ingesta y Salud Integral de Datos.")

listings, sessions = load_parquet_data()

st.subheader("Métricas de Pipeline Básico")
col_a, col_b = st.columns(2)
with col_a:
    render_kpi_card("Volumen Total de Inventario", f"{len(listings):,}")
with col_b:
    render_kpi_card("Eventos Traceables", f"{len(sessions):,}")

# Render 4 Data Engineering Charts
st.markdown("---")
st.subheader("Análisis de Calidad y Volumen (4 KPIs)")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(plot_daily_scrape_volume(), use_container_width=True)
    st.plotly_chart(plot_event_distribution(sessions), use_container_width=True)

with col2:
    st.plotly_chart(plot_data_drift(), use_container_width=True)
    st.plotly_chart(plot_missing_values(listings), use_container_width=True)

render_alert("Data Lake Estable. La densidad Nula es aceptable para Modelado de Features.", type="success")
