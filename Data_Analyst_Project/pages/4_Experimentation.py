import streamlit as st
from utils.data_loader import load_parquet_data
from components.ui_cards import render_alert
from components.charts import *

st.set_page_config(page_title="DS3 Experimentation", page_icon="🧪", layout="wide")

st.header("4. Inteligencia Causal y Crecimiento Estratégico")
st.markdown("Aislamiento estadístico riguroso para medir el impacto real de nuevos features sobre el comportamiento de compra.")

listings, sessions = load_parquet_data()

st.subheader("Resultados del Test A/B: Hook Emocional vs Catálogo Estático (4 KPIs)")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(plot_ab_test_results(sessions), use_container_width=True)
    st.plotly_chart(plot_average_marginal_effects(), use_container_width=True)

with col2:
    st.plotly_chart(plot_confidence_intervals(), use_container_width=True)
    st.plotly_chart(plot_funnel(), use_container_width=True)

render_alert("El Hook Emocional demuestra un uplift causal absoluto robusto (Z-Test > 1.96). La regresión logística (AME) confirma que el video es el feature causal más alto.", type="success")
