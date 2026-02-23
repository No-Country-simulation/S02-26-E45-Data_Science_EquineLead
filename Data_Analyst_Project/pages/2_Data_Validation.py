import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from utils.data_loader import load_parquet_data
from components.ui_cards import render_kpi_card, render_alert

st.set_page_config(page_title="Validación de Datos", page_icon="🔎")

st.header("2. Validación de Datos (Sinergia DE)")
st.markdown("Para que los modelos de Machine Learning funcionen, nuestra métrica GIGO (Garbage In, Garbage Out) debe estar validada mediante la Data real extraída.")

listings, sessions = load_parquet_data()

if listings is not None and sessions is not None:
    col1, col2 = st.columns(2)
    with col1:
        render_kpi_card(title="Volumen de Inventario Procesado", value=f"{len(listings):,}")
    with col2:
        render_kpi_card(title="Sesiones de Usuario Logeadas", value=f"{len(sessions):,}")
        
    st.subheader("Calidad del Inventario (Head Listings)")
    st.dataframe(listings[['Horse_ID', 'Price', 'Age', 'Registry']].head(10))
    
    st.subheader("Comportamiento del Usuario (Distribución de Eventos)")
    events_dist = sessions['event_type'].value_counts(normalize=True).reset_index()
    events_dist.columns = ['Evento', 'Porcentaje']
    events_dist['Porcentaje'] = events_dist['Porcentaje'] * 100
    
    # Simple bar chart
    fig, ax = plt.subplots(figsize=(8, 3))
    plt.style.use('dark_background')
    sns.barplot(data=events_dist, x='Porcentaje', y='Evento', palette='viridis', ax=ax)
    ax.set_title("Distribución de leads crudos frente a rebotes")
    st.pyplot(fig)
else:
    render_alert("No se encontraron los archivos .parquet. Ejecute el pipeline de DE primero.", type="warning")
