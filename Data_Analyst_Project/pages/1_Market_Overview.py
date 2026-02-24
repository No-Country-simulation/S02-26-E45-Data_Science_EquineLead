import streamlit as st
from utils.data_loader import load_parquet_data
from components.ui_cards import render_kpi_card, render_alert
from components.charts import *
from components.sidebar_filters import render_global_filters
from utils.style_utils import inject_bi_style, render_bi_header

st.set_page_config(page_title="Mercado Ecuestre", page_icon="📈", layout="wide")

# Apply BI Style
inject_bi_style()

# Header
render_bi_header("Market Intelligence", "Análisis de Valor y Distribución del Mercado VIP")

# Load & Filter Data
raw_listings, raw_sessions, raw_users = load_parquet_data()
listings, sessions, users = render_global_filters(raw_listings, raw_sessions, raw_users)

# Main KPIs
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("Total Inventario", f"{len(listings):,}")
with col_m2:
    st.metric("Valor Mercado (TAM)", f"${listings['Price'].sum()/1e6:,.1f}M")
with col_m3:
    st.metric("Precio Promedio", f"${listings['Price'].mean():,.0f}")
with col_m4:
    st.metric("Países Activos", f"{len(users['country'].unique()) if 'country' in users.columns else 'N/A'}")

st.markdown("---")

# Visual Insights (Con Segmentadores Locales en las Gráficas)
st.markdown("### 📊 Tablero Interactivo de Mercado")

# Local Slicers right above charts
scol1, scol2, scol3 = st.columns(3)
with scol1:
    chart_view = st.selectbox("📍 [Segmentador de Gráfica] Nivel Geográfico", ["Global", "Top 5 Regiones"])
with scol2:
    price_filter = st.slider("💰 [Segmentador de Gráfica] Rango de Precio Visual", int(listings['Price'].min()), int(listings['Price'].max()), (int(listings['Price'].min()), int(listings['Price'].max())))
with scol3:
    time_grain = st.selectbox("⏱️ [Segmentador de Gráfica] Vista Temporal", ["Mensual", "Trimestral"])

# Apply local chart slicers
filtered_local = listings[(listings['Price'] >= price_filter[0]) & (listings['Price'] <= price_filter[1])]
users_local = users if chart_view == "Global" else users.head(int(len(users)*0.5))

col1, col2 = st.columns([1, 1])

with col1:
    with st.container():
        st.plotly_chart(plot_tam_distribution(users_local), use_container_width=True)
    with st.container():
        st.plotly_chart(plot_traffic_seasonality(time_grain), use_container_width=True)

with col2:
    with st.container():
        st.plotly_chart(plot_price_distribution(filtered_local), use_container_width=True)
    with st.container():
        st.plotly_chart(plot_cpl_comparison(), use_container_width=True)

render_alert("Vista Filtrada: Los segmentadores laterales permiten auditar sub-nichos de alto valor de forma dinámica.")
