import streamlit as st
from components.ui_cards import render_kpi_card, render_alert

st.set_page_config(page_title="Mercado Ecuestre", page_icon="📈")

st.header("1. Valor de Negocio y Mercado Ecuestre")

st.subheader("El Problema Inicial")
st.markdown("""
Antes de la implementación de EquineLead, el mercado online presentaba ineficiencias críticas:
- **Demasiado ruido:** Usuarios navegando cientos de listados técnicos monótonos, generando poco contacto (Conversión del 13.5%).
- **Invisibilidad del segmento VIP:** Caballos con *pedigrí premium* perdidos en búsquedas de usuarios recreacionales.
- **Publicaciones a ciegas:** Se subían listings sin evidencia estadística de qué captaba al comprador.
""")

st.subheader("El Total Addressable Market (TAM)")
render_alert("El mercado global ecuestre está valorado en más de **$300 Billones USD** anuales (American Horse Council).")

col1, col2 = st.columns(2)
with col1:
    render_kpi_card(title="Ticket Promedio (Venta de Caballo)", value="$10,000 USD", help_text="Promedio conservador para caballos deportivos web.")
with col2:
    render_kpi_card(title="Valor del Lead B2B", value="~$15 USD", delta="CPL Estimado", help_text="Lo que EquineLead cobra al establo.")
    
st.markdown("""
### Modelo de Negocio (EquineLead)
Cobramos a los dueños de establos (Criadores) por proporcionarles **Leads Calificados** impulsados por machine learning, a diferencia de los portales antiguos que cobran mensualidades rasas por exhibir clasificados estáticos.
""")
