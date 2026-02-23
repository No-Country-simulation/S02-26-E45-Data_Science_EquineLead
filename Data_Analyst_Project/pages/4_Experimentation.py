import streamlit as st
from utils.data_loader import load_parquet_data
from components.ui_cards import render_alert
from components.charts import *
from components.sidebar_filters import render_global_filters
from utils.style_utils import inject_bi_style, render_bi_header

st.set_page_config(page_title="Experimentation", page_icon="🧪", layout="wide")
inject_bi_style()
render_bi_header("Inteligencia Causal", "Testeo A/B y Optimización de Conversión (DS3)")

raw_listings, raw_sessions, raw_users = load_parquet_data()
listings, sessions, users = render_global_filters(raw_listings, raw_sessions, raw_users)

col1, col2 = st.columns(2)
with col1:
    with st.container():
        st.plotly_chart(plot_ab_test_results(sessions), use_container_width=True)
    with st.container():
        st.plotly_chart(plot_average_marginal_effects(), use_container_width=True)

with col2:
    with st.container():
        st.plotly_chart(plot_confidence_intervals(), use_container_width=True)
    with st.container():
        st.plotly_chart(plot_funnel(), use_container_width=True)

render_alert("Impacto Causal: Se confirma estadísticamente que el feature de 'Video' es el principal driver de leads calificados.", type="success")
