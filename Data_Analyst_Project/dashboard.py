import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="EquineLead: Data Analyst Report", page_icon="🐎", layout="wide")

st.title("🐎 EquineLead: Executive Data Analyst Dashboard")
st.markdown("### De Directorio Estático a Marketplace Inteligente")
st.markdown("Este dashboard interactivo consolida el trabajo de Análisis de Datos, justificando económicamente el esfuerzo del Squad (DE, MLE, DS) mediante KPIs, análisis de mercado y proyecciones de ROI.")

st.sidebar.title("Navegación")
page = st.sidebar.radio("Ir a:", ["1. Valor de Negocio y Mercado", "2. Validación de Materia Prima", "3. Cálculo de KPIs y ROI", "4. Presentación Ejecutiva (Pitch)"])

# Attempt to load data for visualisations
@st.cache_data
def load_data():
    try:
        # Puesto que las carpetas pueden variar dependiendo de donde se corre
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        listings = pd.read_parquet(os.path.join(base_path, 'data/clean/horses_listings_limpio.parquet'))
        sessions = pd.read_parquet(os.path.join(base_path, 'data/clean/horses_sessions_info.parquet'))
        return listings, sessions
    except Exception as e:
        return None, None

listings, sessions = load_data()

if page == "1. Valor de Negocio y Mercado":
    st.header("1. Valor de Negocio y Mercado Ecuestre")
    
    st.subheader("El Problema Inicial")
    st.markdown("""
    Antes de EquineLead, el mercado online presentaba ineficiencias críticas:
    - **Demasiado ruido:** Usuarios navegando cientos de listados, generando poco contacto (Conversión del 13.5%).
    - **Invisibilidad del segmento VIP:** Caballos con *pedigrí premium* perdidos en búsquedas de usuarios recreacionales.
    - **Publicaciones a ciegas:** Se subían listings sin evidencia de qué captaba al comprador.
    """)
    
    st.subheader("El Total Addressable Market (TAM)")
    st.info("El mercado global ecuestre vale más de **$300 Billones USD** anuales.")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Ticket Promedio (Venta de Caballo)", value="$10,000 USD")
    with col2:
        st.metric(label="Valor del Lead B2B", value="~$15 USD", delta="CPL Estimado")
        
    st.markdown("""
    **Modelo de Negocio:** Cobramos a los dueños de establos (Criadores) por proporcionarles *Leads Calificados* impulsados por machine learning, a diferencia de los portales antiguos que cobran mensualidades rasas por exhibir clasificados estáticos.
    """)

elif page == "2. Validación de Materia Prima":
    st.header("2. Validación de Datos (Sinergia con Data Engineering)")
    st.markdown("Para que los modelos de Machine Learning funcionen, nuestra métrica GIGO (Garbage In, Garbage Out) debe estar validada.")
    
    if listings is not None and sessions is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Volumen de Inventario Procesado", value=f"{len(listings):,}")
        with col2:
            st.metric(label="Sesiones de Usuario Logeadas", value=f"{len(sessions):,}")
            
        st.subheader("Calidad del Inventario (Listings)")
        st.dataframe(listings[['Horse_ID', 'Price', 'Age', 'Registry']].head(10))
        
        st.subheader("Comportamiento del Usuario (Eventos)")
        events_dist = sessions['event_type'].value_counts(normalize=True).reset_index()
        events_dist.columns = ['Evento', 'Porcentaje']
        events_dist['Porcentaje'] = events_dist['Porcentaje'] * 100
        
        # Simple bar chart
        fig, ax = plt.subplots(figsize=(6, 3))
        sns.barplot(data=events_dist, x='Porcentaje', y='Evento', palette='viridis', ax=ax)
        st.pyplot(fig)
        
    else:
        st.warning("No se encontraron los archivos .parquet localmente en la carpeta de datos para renderizar la validación viva.")

elif page == "3. Cálculo de KPIs y ROI":
    st.header("3. Retorno de Inversión y Modelado Financiero")
    
    st.markdown("### Simulador Dinámico de ROI")
    st.markdown("Usando el **+16.2% de uplift predictivo** validado por Experimentación (DS3).")
    
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
        st.metric("Leads Extra (Generados por ML)", f"+{leads_extra:,}")
    with col2:
        st.metric("Ingreso Neto Adicional", f"${(leads_extra * costo_lead):,.0f}")
    with col3:
        st.metric("ROI Mensual Proyectado", f"{roi:,.0f}%")
        
    st.markdown("---")
    st.subheader("Proyección a 6 Meses")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    meses = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']
    costos = [costo_squad]*6
    # Simulamos adopción escalada de leads (40%, 60%, 80%, 100%...)
    ingresos = [((leads_extra * 0.5) * costo_lead), ((leads_extra * 0.7) * costo_lead), 
                ((leads_extra * 0.9) * costo_lead), (leads_extra * costo_lead), 
                (leads_extra * costo_lead), (leads_extra * 1.1 * costo_lead)]
    neto = [i - c for i, c in zip(ingresos, costos)]
    
    ax.plot(meses, ingresos, label="Ingreso Extra Bruto", color="gold", marker='o')
    ax.plot(meses, costos, label="Costos Base (Squad+Infra)", color="red", linestyle="--")
    ax.bar(meses, neto, alpha=0.3, label="Profit Neto (ROI)", color="green")
    ax.legend()
    st.pyplot(fig)

elif page == "4. Presentación Ejecutiva (Pitch)":
    st.header("4. El Pitch Final (Alineación Ejecutiva)")
    st.markdown("### EquineLead: La Máquina de Monetizar Datos")
    
    st.markdown("""
    **1. Dónde estábamos (El Problema):**
    Una plataforma estática con una tasa baja y estancada de contactos (~13%). La información de calidad premium competía ineficazmente con caballos recreacionales por falta de filtros algorítmicos.
    
    **2. La Evolución (Nuestra Solución Tecnológica):**
    *   **Data Engineering:** Reemplazó el proceso manual y ahora captura el pulso del mercado real 24/7 sin fallos (Scrapers robustos).
    *   **Machine Learning (DS1/MLE):** Modeló características predictivas y creó *Recomendaciones Dinámicas*, logrando empaquetar estos insights en un dashboard/API escalable.
    *   **Experimentación (DS3):** Sometió intuiciones al rigor empírico. Encontramos que un *Hook Emocional* incrementa masivamente el contacto en nuestro canal masivo, y validamos que el comportamiento pasado (vistas) es el rey sobre atributos estáticos como el precio.
    
    **3. El Impacto Económico:**
    Ajustar estos engranajes aumentó de inmediato el embudo central en un **+16% relativo (Uplift absoluto de >2% general)**. En términos monetizados (vendiendo visibilidad calificada B2B), justifica por sí solo el costo de infraestructura (Nube, APIs) y del equipo completo de datos de la compañía, entregando un ROI superior al **500%** al mes.
    
    **Conclusión:**
    EquineLead dejó de ser un sitio web. Ahora es un sistema de predicción financiera validado empíricamente, escalable, y lo más importante: **altamente rentable**.
    """)
    st.success("¡Pitch Ejecutivo completado con éxito! ✅")
