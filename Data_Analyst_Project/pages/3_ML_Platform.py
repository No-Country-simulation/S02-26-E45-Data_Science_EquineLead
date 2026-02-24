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
    algo = st.selectbox("🧠 Algoritmo Benchmark", ["Random Forest", "XGBoost", "Logistic Regression"])
with scol2:
    threshold = st.slider("📏 Umbral de Probabilidad", 0.1, 0.9, 0.5, step=0.05)
with scol3:
    metric = st.selectbox("🎯 Métrica de Evaluación Primaria", ["ROC AUC", "Precision", "Recall", "F1 Score"])

st.markdown("---")

# Dynamic Metrics based on Algorithm and Primary Metric
if algo == "Random Forest":
    auc, prec, rec, f1 = 0.89, 0.82, 0.78, 0.79
elif algo == "XGBoost":
    auc, prec, rec, f1 = 0.92, 0.85, 0.81, 0.83
else:
    auc, prec, rec, f1 = 0.78, 0.71, 0.65, 0.68

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    metric_map = dict(zip(['ROC AUC', 'Precision', 'Recall', 'F1 Score'], ['auc', 'prec', 'rec', 'f1']))
    st.metric(f"🏆 {metric}", f"{locals()[metric_map[metric]] * 100:.1f}%")
with m_col2:
    st.metric("Curva ROC (AUC)", f"{auc:.2f}")
with m_col3:
    st.metric("Precisión (Falsos +)", f"{prec:.2f}")
with m_col4:
    st.metric("Recall (Captura Real)", f"{rec:.2f}")

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    with st.container():
        st.plotly_chart(plot_feature_importance(algo), use_container_width=True)
    with st.container():
        st.plotly_chart(plot_roc_curve(algo), use_container_width=True)

with col2:
    with st.container():
        st.plotly_chart(plot_predicted_probabilities(sessions), use_container_width=True)
    with st.container():
        st.plotly_chart(plot_confusion_matrix(threshold), use_container_width=True)

render_alert("Comportamiento Algorítmico: El modelo de propensión demuestra estabilidad ante el ruido de datos reales.", type="info")
