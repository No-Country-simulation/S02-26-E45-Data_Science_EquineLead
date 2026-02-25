import streamlit as st
from components.ui_cards import render_kpi_card, render_alert
from components.charts import *

st.set_page_config(page_title="Executive ROI", page_icon="💸", layout="wide")

st.header("5. Retorno de Inversión y Modelado Financiero")
st.markdown("### Motor de Simulación Financiera Escalable")
render_alert("Integrando el **+16.2% de uplift predictivo** para calcular el impacto en el Gross Revenue Corporativo.")

# Sliders para simulacion de negocio
st.sidebar.markdown("---")
st.sidebar.markdown("### Parámetros Financieros (Simulador)")
tráfico = st.sidebar.slider("Tráfico Mensual (Sesiones)", 50000, 500000, 200000, step=10000)
costo_lead = st.sidebar.slider("Precio Cobrado por Lead B2B (USD)", 5, 50, 15, step=1)
costo_squad = st.sidebar.slider("Opex Mensual (Squad Data+Cloud) (USD)", 5000, 50000, 10000, step=1000)

conv_base = 0.1349
conv_optimizada = 0.1568

leads_base = int(tráfico * conv_base)
leads_nuevos = int(tráfico * conv_optimizada)
leads_extra = leads_nuevos - leads_base
profit = (leads_extra * costo_lead) - costo_squad
roi = (profit / costo_squad) * 100

st.subheader("Gross Impact Directo")
col1, col2, col3 = st.columns(3)
with col1:
    render_kpi_card("Leads Extra (Generados por ML)", f"+{leads_extra:,}")
with col2:
    render_kpi_card("Ingreso Neto Adicional", f"${(leads_extra * costo_lead):,.0f}")
with col3:
    render_kpi_card("ROI Mensual Proyectado", f"{roi:,.0f}%")

st.markdown("---")
st.subheader("Análisis de Riesgo y Escalabilidad (4 Gráficos)")

col_a, col_b = st.columns(2)
with col_a:
    meses = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']
    ingresos = [((leads_extra * 0.5) * costo_lead), ((leads_extra * 0.7) * costo_lead), 
                ((leads_extra * 0.9) * costo_lead), (leads_extra * costo_lead), 
                (leads_extra * costo_lead), (leads_extra * 1.1 * costo_lead)]
    st.plotly_chart(plot_roi_projection(costo_squad, ingresos, meses), use_container_width=True)
    st.plotly_chart(plot_break_even(), use_container_width=True)

with col_b:
    st.plotly_chart(plot_ltv(), use_container_width=True)
    st.plotly_chart(plot_profit_margin(), use_container_width=True)

st.success("🎉 Pitch Ejecutivo completado. El Dashboard profesional enruta todas las ramas (DS3, ML-Platform, Infra) en un solo flujo de Revenue validado.")
