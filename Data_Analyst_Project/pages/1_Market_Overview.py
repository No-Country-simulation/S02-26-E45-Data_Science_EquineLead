import streamlit as st
from utils.data_loader import load_parquet_data
from components.ui_cards import render_kpi_card, render_alert
from components.charts import *

st.set_page_config(page_title="Mercado Ecuestre", page_icon="📈", layout="wide")

st.header("1. Valor de Negocio y Mercado Ecuestre (Core Business)")

st.subheader("El Problema Inicial")
st.markdown("""
Antes de la implementación de EquineLead, el mercado online presentaba ineficiencias críticas:
- **Demasiado ruido:** Usuarios navegando cientos de listados técnicos monótonos, generando poco contacto (Conversión del 13.5%).
- **Invisibilidad del segmento VIP:** Caballos con pedigrí premium perdidos en búsquedas de usuarios recreacionales.
""")

listings, sessions, users = load_parquet_data()

st.subheader("Análisis Macro-Económico (4 KPIs)")
# Render 4 Charts from charts.py
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(plot_tam_distribution(listings, users), use_container_width=True)
    st.plotly_chart(plot_traffic_seasonality(), use_container_width=True)

with col2:
    st.plotly_chart(plot_cpl_comparison(), use_container_width=True)
    st.plotly_chart(plot_price_distribution(listings), use_container_width=True)

st.markdown("---")
render_alert("Modelo de Negocio validado: Transición de cobro por Suscripción Estática a cobro dinámico por Leads Calificados impulsados por ML.")
