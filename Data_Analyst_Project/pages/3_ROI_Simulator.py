import streamlit as st
from components.ui_cards import render_kpi_card, render_alert
from components.charts import plot_roi_projection, plot_conversion_impact

st.set_page_config(page_title="Retorno de Inversión", page_icon="💸")

st.header("3. Retorno de Inversión y Modelado Financiero")
st.markdown("### Simulador Dinámico de ROI")
render_alert("Usando el **+16.2% de uplift predictivo** validado por Experimentación (DS3).")

# Sliders para simulacion de negocio
st.sidebar.markdown("---")
st.sidebar.markdown("### Parámetros del Simulador")
tráfico = st.sidebar.slider("Tráfico Mensual (Sesiones)", 50000, 500000, 200000, step=10000)
costo_lead = st.sidebar.slider("Precio Cobrado por Lead (USD)", 5, 50, 15, step=1)
costo_squad = st.sidebar.slider("Costo Mensual de ML/Cloud (USD)", 5000, 50000, 10000, step=1000)

conv_base = 0.1349
conv_optimizada = 0.1568

leads_base = int(tráfico * conv_base)
leads_nuevos = int(tráfico * conv_optimizada)
leads_extra = leads_nuevos - leads_base

profit = (leads_extra * costo_lead) - costo_squad
roi = (profit / costo_squad) * 100

col1, col2, col3 = st.columns(3)
with col1:
    render_kpi_card("Leads Extra (Generados por ML)", f"+{leads_extra:,}")
with col2:
    render_kpi_card("Ingreso Neto Adicional", f"${(leads_extra * costo_lead):,.0f}")
with col3:
    render_kpi_card("ROI Mensual Proyectado", f"{roi:,.0f}%")

st.markdown("---")
col4, col5 = st.columns(2)

with col4:
    # A/B Test impact Plot
    st.subheader("Impacto A/B Test Validado")
    fig_conv = plot_conversion_impact(conv_base*100, conv_optimizada*100)
    st.pyplot(fig_conv)

with col5:
    # ROI Plot
    st.subheader("Proyección a 6 Meses")
    meses = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']
    ingresos = [((leads_extra * 0.5) * costo_lead), ((leads_extra * 0.7) * costo_lead), 
                ((leads_extra * 0.9) * costo_lead), (leads_extra * costo_lead), 
                (leads_extra * costo_lead), (leads_extra * 1.1 * costo_lead)]
                
    fig_roi = plot_roi_projection(costo_squad, ingresos, meses)
    st.pyplot(fig_roi)
