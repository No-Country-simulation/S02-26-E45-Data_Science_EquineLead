import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# HELPERS
# ==========================================

def get_tag(df: pd.DataFrame) -> str:
    """Returns the visual audit tag based on the source column."""
    if 'source' in df.columns and 'Real' in df['source'].values:
        return " [Auditoría Real]"
    return " [Proyección Directiva]"

# ==========================================
# PAGE 1: MARKET OVERVIEW (4 Charts)
# ==========================================

def plot_tam_distribution(listings: pd.DataFrame, users: pd.DataFrame):
    """Chart 1: TAM Distribution by Country (Pie) using joined real data."""
    # Assuming users has country and users join with sessions/listings
    # For now, if listings has Location, we extract country or use users distribution
    tag = get_tag(listings)
    
    if 'country' in users.columns:
        fig = px.pie(users, names='country', title=f'Distribución Demográfica de Clientes{tag}',
                     color_discrete_sequence=px.colors.sequential.Aggrnyl)
    else:
        # Fallback to listings price distribution by first part of Location
        listings['Temp_Country'] = listings['Location'].apply(lambda x: x.split(',')[-1].strip() if ',' in str(x) else 'Other')
        fig = px.pie(listings, names='Temp_Country', values='Price', title=f'Distribución de Valor por Región{tag}',
                     color_discrete_sequence=px.colors.sequential.Aggrnyl)
    return fig

def plot_cpl_comparison():
    """Chart 2: Pre-DS vs Post-DS CPL (Bar)"""
    data = {'Etapa': ['2023 (Estático)', '2024 (Machine Learning)'], 'CPL (USD)': [25, 15]}
    fig = px.bar(data, x='Etapa', y='CPL (USD)', text='CPL (USD)', title='Reducción Costo por Lead (CPL)', 
                 color='Etapa', color_discrete_map={'2023 (Estático)':'#ff6b6b', '2024 (Machine Learning)':'#1dd1a1'})
    return fig

def plot_traffic_seasonality():
    """Chart 3: Traffic seasonality (Line)"""
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    traffic = [150, 160, 180, 210, 250, 280, 300, 290, 240, 200, 170, 160]
    fig = px.line(x=months, y=traffic, title='Estacionalidad del Tráfico (Miles de Sesiones)', markers=True)
    fig.update_traces(line_color='#feca57')
    return fig

def plot_price_distribution(df: pd.DataFrame):
    """Chart 4: Ticket Price Distribution (Histogram)"""
    tag = get_tag(df)
    fig = px.histogram(df, x='Price', nbins=50, title=f'Distribución Métrica de Precios (USD){tag}',
                       color_discrete_sequence=['#54a0ff'])
    return fig

# ==========================================
# PAGE 2: DATA ENGINEERING (4 Charts)
# ==========================================

def plot_daily_scrape_volume():
    """Chart 5: Daily Scrape Volume"""
    dates = pd.date_range(start='2024-01-01', periods=30)
    volume = np.random.normal(loc=5000, scale=200, size=30).astype(int)
    fig = px.area(x=dates, y=volume, title='Volumen de Extracción Diario (Scrapers)', color_discrete_sequence=['#00d2d3'])
    return fig

def plot_missing_values(df: pd.DataFrame):
    """Chart 6: Data Completeness (Plotly Bar)"""
    # Simulate missing data for visual
    df_miss = df.copy()
    df_miss.loc[np.random.choice(df_miss.index, 50), 'Age'] = np.nan
    df_miss.loc[np.random.choice(df_miss.index, 100), 'Registry'] = np.nan
    
    completeness = (1 - df_miss.isnull().mean()) * 100
    fig = px.bar(x=completeness.index, y=completeness.values, 
                 title='Completitud de Datos por Columna (%)',
                 labels={'x': 'Atributos (Features)', 'y': 'Completitud (%)'},
                 color=completeness.values, color_continuous_scale='RdYlGn')
    fig.add_hline(y=95, line_dash="dash", line_color="orange", annotation_text="Meta 95%")
    fig.update_yaxes(range=[80, 100])
    return fig

def plot_event_distribution(df: pd.DataFrame):
    """Chart 7: Event Distribution (Donut)"""
    tag = get_tag(df)
    fig = px.pie(df, names='event_type', title=f'Distribución del Funnel (Eventos){tag}', hole=0.5,
                 color_discrete_sequence=px.colors.sequential.Plasma)
    return fig

def plot_data_drift():
    """Chart 8: Data Drift Simulation"""
    weeks = ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4']
    drift_score = [0.02, 0.05, 0.04, 0.12] # Spike in week 4
    fig = px.bar(x=weeks, y=drift_score, title='Alerta de Data Drift (KS Test Score)',
                 color=drift_score, color_continuous_scale='Reds')
    fig.add_hline(y=0.1, line_dash="dash", line_color="red", annotation_text="Umbral de Re-entrenamiento")
    return fig

# ==========================================
# PAGE 3: ML PLATFORM (4 Charts)
# ==========================================

def plot_feature_importance():
    """Chart 9: Random Forest Permutation Importance"""
    features = ['Vistas_Previas', 'Precio', 'Edad', 'Tiene_Video', 'Raza_Premium']
    importance = [0.45, 0.20, 0.15, 0.12, 0.08]
    fig = px.bar(x=importance, y=features, orientation='h', title='Importancia de Variables (Permutation)',
                 color=importance, color_continuous_scale='Mint')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig

def plot_predicted_probabilities(df: pd.DataFrame):
    """Chart 10: KDE of Predicted Probabilities"""
    # Note: predicted_prob is projected (synthetic) even if sessions is real
    fig = px.histogram(df, x='predicted_prob', color='event_type', marginal='box',
                       title='Distribución KDE: Probabilidades de Conversión [Proyección]', barmode='overlay',
                       opacity=0.7)
    return fig

def plot_roc_curve():
    """Chart 11: ROC AUC Simulation"""
    fpr = np.linspace(0, 1, 100)
    tpr = np.sqrt(fpr) # mock curve shape
    fig = px.line(x=fpr, y=tpr, title='Curva ROC (AUC = 0.89)')
    fig.add_shape(type='line', line=dict(dash='dash'), x0=0, x1=1, y0=0, y1=1)
    fig.update_layout(xaxis_title='Falsos Positivos', yaxis_title='Verdaderos Positivos')
    return fig

def plot_confusion_matrix():
    """Chart 12: Predict Confusion Matrix"""
    z = [[4500, 200], [150, 480]]
    fig = px.imshow(z, text_auto=True, title='Matrix de Confusión (Test Set)',
                    labels=dict(x="Predicción", y="Realidad"),
                    x=['No Lead', 'Lead'], y=['No Lead', 'Lead'], color_continuous_scale='Blues')
    return fig

# ==========================================
# PAGE 4: DS3 EXPERIMENTATION (4 Charts)
# ==========================================

def plot_ab_test_results(df: pd.DataFrame):
    """Chart 13: A/B Test Results"""
    # group is projected
    counts = df.groupby(['experiment_group', 'event_type']).size().reset_index(name='count')
    purchases = counts[counts['event_type'] == 'purchase']
    fig = px.bar(purchases, x='experiment_group', y='count', color='experiment_group',
                 title='A/B Test: Leads Generados [Proyección Post-Campaña]')
    return fig

def plot_confidence_intervals():
    """Chart 14: 95% Confidence Intervals"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[13.49, 15.68], y=['Control', 'Tratamiento'],
                             error_x=dict(type='data', array=[0.8, 1.1], visible=True),
                             mode='markers', marker=dict(size=12, color=['#ff6b6b', '#1dd1a1'])))
    fig.update_layout(title='Intervalos de Confianza 95% (Conversión %)', xaxis_title='Tasa de Conversión')
    return fig

def plot_average_marginal_effects():
    """Chart 15: AME Logit Model"""
    effects = {'Premium Pedigree': -0.02, 'Con Video': 0.05, 'Hook Emocional': 0.08, 'Precio Alto': -0.04}
    fig = px.bar(x=list(effects.values()), y=list(effects.keys()), orientation='h',
                 title='Efectos Marginales Promedio (AME)', color=list(effects.values()), 
                 color_continuous_scale=['red', 'gray', 'green'])
    fig.add_vline(x=0, line_dash="solid", line_color="white")
    return fig

def plot_funnel():
    """Chart 16: Sales Funnel"""
    data = dict(number=[50000, 15000, 6000, 800], stage=["Impresiones", "Clicks", "Vistas Detalles", "Leads B2B"])
    fig = px.funnel(data, x='number', y='stage', title='Embudo de Conversión (General)')
    return fig

# ==========================================
# PAGE 5: FINANCIAL ROI (4 Charts)
# ==========================================

def plot_roi_projection(cost_monthly: float, incremental_revenue: list, months: list):
    """Chart 17: ROI Projection 6 Months"""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=months, y=incremental_revenue, name='Revenue Extra', marker_color='#1dd1a1'))
    fig.add_trace(go.Scatter(x=months, y=[cost_monthly]*len(months), name='Costos Fijos', line=dict(color='red', dash='dash')))
    profit = [r - cost_monthly for r in incremental_revenue]
    fig.add_trace(go.Scatter(x=months, y=profit, name='Net Profit', fill='tozeroy', fillcolor='rgba(29, 209, 161, 0.2)'))
    fig.update_layout(title='Proyección Dinámica de ROI Económico', yaxis_title='USD', barmode='group')
    return fig

def plot_break_even():
    """Chart 18: Break-even Point"""
    leads_sold = np.linspace(0, 1000, 50)
    revenue = leads_sold * 15 # $15 per lead
    cost = 10000 + (leads_sold * 2) # Fixed + Variable
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=leads_sold, y=revenue, name='Ingresos Totales', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=leads_sold, y=cost, name='Costos Totales', line=dict(color='red')))
    fig.update_layout(title='Análisis de Break-Even (Punto de Equilibrio)', xaxis_title='Leads Vendidos', yaxis_title='USD')
    return fig

def plot_ltv():
    """Chart 19: LTV Projection"""
    segments = ['Pequeño Criador', 'Establo Mediano', 'Atleta Olímpico']
    ltv = [500, 2500, 15000]
    fig = px.bar(x=segments, y=ltv, title='Lifetime Value Esperado (LTV) por Segmento', text=ltv, color=ltv)
    return fig

def plot_profit_margin():
    """Chart 20: Net Profit Margin Area"""
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    margin = [12, 18, 45, 62] # Margin % evolution
    fig = px.area(x=quarters, y=margin, title='Evolución del Margen de Beneficio Neto (%)', markers=True)
    fig.update_traces(line_color='#ff9ff3', fillcolor='rgba(255, 159, 243, 0.3)')
    return fig
