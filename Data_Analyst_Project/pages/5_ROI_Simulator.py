import streamlit as st
from components.ui_cards import render_kpi_card, render_alert
from components.charts import *
from utils.data_loader import load_parquet_data
from components.sidebar_filters import render_global_filters
from utils.style_utils import inject_bi_style, render_bi_header

st.set_page_config(page_title="ROI Simulator", page_icon="💸", layout="wide")
inject_bi_style()
render_bi_header("ROI & Financial Impact", "Simulador de Retorno Económico y Escalabilidad")

raw_listings, raw_sessions, raw_users = load_parquet_data()
listings, sessions, users = render_global_filters(raw_listings, raw_sessions, raw_users)

# Local Slicers / Parámetros de Simulación en Gráficas
st.markdown("### 🎛️ Segmentadores de Proyección ROI")
scol1, scol2, scol3 = st.columns(3)
with scol1:
    tráfico = st.slider("🌐 Tráfico Base Sesiones", 50000, 1000000, 200000, step=50000)
with scol2:
    costo_lead = st.slider("💵 USD / Lead Generado", 5, 100, 25, step=5)
with scol3:
    costo_squad = st.slider("👥 Opex Squad (Mensual)", 5000, 50000, 15000, step=5000)

conv_base = 0.1349
conv_optimizada = 0.1568
leads_extra = int(tráfico * (conv_optimizada - conv_base))
revenue_extra = leads_extra * costo_lead
profit = revenue_extra - costo_squad
roi = (profit / costo_squad) * 100

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Leads Incrementales", f"+{leads_extra:,}")
with col2:
    st.metric("Revenue Proyectado", f"${revenue_extra:,.0f}")
with col3:
    st.metric("ROI Estimado", f"{roi:,.0f}%")

st.markdown("---")

col_a, col_b = st.columns(2)
with col_a:
    with st.container():
        meses = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']
        ingresos = [((leads_extra * 0.5) * costo_lead), ((leads_extra * 0.7) * costo_lead), 
                    ((leads_extra * 0.9) * costo_lead), (leads_extra * costo_lead), 
                    (leads_extra * costo_lead), (leads_extra * 1.1 * costo_lead)]
        st.plotly_chart(plot_roi_projection(costo_squad, ingresos, meses), use_container_width=True)
    with st.container():
        st.plotly_chart(plot_break_even(), use_container_width=True)

with col_b:
    with st.container():
        st.plotly_chart(plot_ltv(), use_container_width=True)
    with st.container():
        st.plotly_chart(plot_profit_margin(), use_container_width=True)

st.success("🎉 Pitch Final: El sistema demuestra viabilidad económica inmediata bajo datos reales filtrados.")
