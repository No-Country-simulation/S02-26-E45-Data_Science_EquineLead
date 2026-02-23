import streamlit as st
import pandas as pd
from utils.data_loader import load_parquet_data
from components.ui_cards import render_alert
from components.charts import *

st.set_page_config(page_title="Machine Learning", page_icon="🤖", layout="wide")

st.header("3. Motor Predictivo de Inteligencia Artificial")
st.markdown("Auditoría estadística del Algoritmo de Lead Scoring y su capacidad de generalización productiva.")

listings, sessions, users = load_parquet_data()

st.subheader("Performance del Modelo Predictivo (4 Gráficos)")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(plot_feature_importance(), use_container_width=True)
    st.plotly_chart(plot_roc_curve(), use_container_width=True)

with col2:
    st.plotly_chart(plot_predicted_probabilities(sessions), use_container_width=True)
    st.plotly_chart(plot_confusion_matrix(), use_container_width=True)

render_alert("El Tracker indica que el algoritmo general retiene un ROC-AUC de 0.89 en datos invisibles (Test Set). Comportamiento robusto para producción.", type="info")
