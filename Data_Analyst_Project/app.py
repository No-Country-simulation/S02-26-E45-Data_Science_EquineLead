import streamlit as st
from utils.style_utils import inject_bi_style, render_bi_header
from components.ui_cards import render_alert

st.set_page_config(page_title="EquineLead Dashboard", page_icon="🐎", layout="wide")

# Apply Aesthetics
inject_bi_style()

# Hero Section
st.image("https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
render_bi_header("EquineLead Executive Hub", "Dashboard de Inteligencia de Negocios y Ciencia de Datos")

st.markdown("""
### Visión General del Ecosistema
Este dashboard integra **Auditoría de Datos en Tiempo Real** con **Capacidades Predictivas** para optimizar el mercado ecuestre B2B.

---
""")

# Professional Cards for Navigation
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: rgba(59, 130, 246, 0.1); padding: 20px; border-radius: 12px; border: 1px solid #3b82f6;">
        <h3 style="color: #60a5fa;">📈 Market Oversight</h3>
        <p style="color: #94a3b8;">Análisis de valor real del inventario y segmentación demográfica auditada bajo estándares de BI.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(16, 185, 129, 0.1); padding: 20px; border-radius: 12px; border: 1px solid #10b981;">
        <h3 style="color: #34d399;">🤖 ML Engine</h3>
        <p style="color: #94a3b8;">Lead Scoring predictivo con un ROC-AUC de 0.89 validado sobre el Data Lake de producción.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: rgba(251, 191, 36, 0.1); padding: 20px; border-radius: 12px; border: 1px solid #fbbf24;">
        <h3 style="color: #fbbf24;">💸 ROI Simulator</h3>
        <p style="color: #94a3b8;">Simulación financiera dinámica del impacto directo en el Revenue Corporativo escalable.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
render_alert("Estado de Plataforma: Ecosistema Midnight Glass activo. Datos auditados en tiempo real.", type="info")

st.sidebar.markdown("---")
st.sidebar.info("Navegación Ejecutiva Activa")
