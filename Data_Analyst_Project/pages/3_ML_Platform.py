import streamlit as st
from utils.data_loader import load_parquet_data
from components.ui_cards import render_alert
from components.charts import *
from components.sidebar_filters import render_global_filters
from utils.style_utils import inject_bi_style, render_bi_header

st.set_page_config(page_title="ML Platform", page_icon="🤖", layout="wide")
inject_bi_style()
render_bi_header("ML & Lead Scoring", "Auditoría Predictiva y Performance de Algoritmos")

raw_listings, raw_sessions, raw_users = load_parquet_data()
listings, sessions, users = render_global_filters(raw_listings, raw_sessions, raw_users)

st.markdown("### 🎛️ Parámetros del Modelo")
scol1, scol2, scol3 = st.columns(3)
with scol1:
    st.selectbox("🧠 Algoritmo Benchmark", ["Random Forest", "XGBoost", "Logistic Regression"])
with scol2:
    st.slider("📏 Umbral de Probabilidad", 0.1, 0.9, 0.5, step=0.05)
with scol3:
    st.selectbox("🎯 Métrica de Evaluación Primaria", ["ROC AUC", "Precision", "Recall", "F1 Score"])

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    with st.container():
        st.plotly_chart(plot_feature_importance(), use_container_width=True)
    with st.container():
        st.plotly_chart(plot_roc_curve(), use_container_width=True)

with col2:
    with st.container():
        st.plotly_chart(plot_predicted_probabilities(sessions), use_container_width=True)
    with st.container():
        st.plotly_chart(plot_confusion_matrix(), use_container_width=True)

render_alert("Comportamiento Algorítmico: El modelo de propensión demuestra estabilidad ante el ruido de datos reales.", type="info")
