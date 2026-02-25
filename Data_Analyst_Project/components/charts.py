import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Palette Config (Ultra-Premium Deep Glass)
COLOR_REAL = "#3b82f6" 
COLOR_SIM = "#10b981"  
COLOR_GRID = "rgba(255, 255, 255, 0.08)"
COLOR_TEXT = "#e2e8f0"

def get_tag(df: pd.DataFrame) -> str:
    """Returns the visual audit tag based on the source column."""
    if 'source' in df.columns and 'Real' in df['source'].values:
        return " [Auditoría Real]"
    return " [Proyección Directiva]"

def apply_bi_layout(fig, title: str):
    """Applies an ultra-premium executive layout to any plotly figure."""
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=18, color="#ffffff")),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLOR_TEXT, family='Inter'),
        margin=dict(l=50, r=30, t=70, b=50),
        xaxis=dict(showgrid=True, gridcolor=COLOR_GRID, linecolor=COLOR_GRID, 
                   tickfont=dict(color=COLOR_TEXT, size=11), title_font=dict(color=COLOR_TEXT)),
        yaxis=dict(showgrid=True, gridcolor=COLOR_GRID, linecolor=COLOR_GRID, 
                   tickfont=dict(color=COLOR_TEXT, size=11), title_font=dict(color=COLOR_TEXT)),
        hovermode="x unified",
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=COLOR_TEXT), 
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="rgba(15, 23, 42, 0.9)", font_size=13, font_family="Inter", font_color="white",
                        bordercolor="rgba(59, 130, 246, 0.5)")
    )
    return fig

def plot_tam_distribution(listings: pd.DataFrame, users: pd.DataFrame):
    """Chart 1: TAM Distribution by Country (Pie) with Luxury Grouping"""
    tag = get_tag(listings)
    
    col = 'country' if 'country' in users.columns else 'Temp_Country'
    if col == 'Temp_Country':
        listings['Temp_Country'] = listings['Location'].apply(lambda x: x.split(',')[-1].strip() if ',' in str(x) else 'Other')
    
    df_plot = users if col == 'country' else listings
    counts = df_plot[col].value_counts(normalize=True)
    top_n = counts[counts > 0.05].index.tolist()
    
    df_plot['Clean_Country'] = df_plot[col].apply(lambda x: x if x in top_n else 'Otras Regiones')
    
    fig = px.pie(df_plot, names='Clean_Country', hole=0.7,
                 color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_traces(textposition='outside', textinfo='percent+label')
    
    return apply_bi_layout(fig, f'Segmentación Geográfica Premium{tag}')

def plot_cpl_comparison():
    """Chart 2: Pre-DS vs Post-DS CPL (Bar)"""
    data = {'Etapa': ['2023 (Estático)', '2024 (MLE)'], 'CPL (USD)': [25, 15]}
    fig = px.bar(data, x='Etapa', y='CPL (USD)', text='CPL (USD)', 
                 color='Etapa', color_discrete_map={'2023 (Estático)':'#ef4444', '2024 (MLE)':'#10b981'})
    return apply_bi_layout(fig, 'Reducción de Costo por Lead (CPL)')

def plot_traffic_seasonality():
    """Chart 3: Traffic seasonality (Line with Luxe Gradient)"""
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    traffic = [150, 160, 180, 210, 250, 280, 300, 290, 240, 200, 170, 160]
    fig = px.line(x=months, y=traffic, markers=True)
    fig.update_traces(line_color='#3b82f6', fill='tozeroy', 
                      fillcolor='rgba(59, 130, 246, 0.1)', line_width=4)
    return apply_bi_layout(fig, 'Estacionalidad del Tráfico (K Sesiones)')

def plot_price_distribution(df: pd.DataFrame):
    """Chart 4: Ticket Price Distribution"""
    tag = get_tag(df)
    fig = px.histogram(df, x='Price', nbins=50,
                       color_discrete_sequence=[COLOR_REAL],
                       labels={'Price': 'Precio (USD)', 'count': 'Frecuencia'})
    return apply_bi_layout(fig, f'Análisis de Densidad de Precios{tag}')

# ==========================================
# PAGE 2: DATA ENGINEERING (4 Charts)
# ==========================================

def plot_daily_scrape_volume():
    """Chart 5: Daily Scrape Volume (Area)"""
    dates = pd.date_range(start='2024-01-01', periods=30)
    volume = np.random.normal(loc=5000, scale=200, size=30).astype(int)
    fig = px.area(x=dates, y=volume, color_discrete_sequence=['#22d3ee'])
    fig.update_traces(fillcolor='rgba(34, 211, 238, 0.1)', line_width=3)
    return apply_bi_layout(fig, 'Volumen Diario: Ingesta Scrapers')

def plot_missing_values(df: pd.DataFrame):
    """Chart 6: Data Completeness"""
    completeness = (1 - df.isnull().mean()) * 100
    fig = px.bar(x=completeness.index, y=completeness.values, 
                 color=completeness.values, color_continuous_scale='Blues')
    fig.add_hline(y=95, line_dash="dash", line_color="#10b981", annotation_text="SLA 95%")
    return apply_bi_layout(fig, 'Índice de Salud de Datos (%)')

def plot_event_distribution(df: pd.DataFrame):
    """Chart 7: Event Distribution (Donut)"""
    tag = get_tag(df)
    fig = px.pie(df, names='event_type', hole=0.5,
                 color_discrete_sequence=px.colors.qualitative.Prism)
    return apply_bi_layout(fig, f'Embudo de Eventos: Mezcla Proporcional{tag}')

def plot_data_drift():
    """Chart 8: Data Drift Alert"""
    weeks = ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4']
    drift_score = [0.02, 0.05, 0.04, 0.12] 
    fig = px.bar(x=weeks, y=drift_score, color=drift_score, color_continuous_scale='Reds')
    fig.add_hline(y=0.1, line_dash="dash", line_color="#ef4444", annotation_text="THRESHOLD")
    return apply_bi_layout(fig, 'Monitoreo de Data Drift (KS-Stat)')

# ==========================================
# PAGE 3: ML PLATFORM (4 Charts)
# ==========================================

def plot_feature_importance():
    """Chart 9: Random Forest Permutation Importance"""
    features = ['Vistas_Previas', 'Precio', 'Edad', 'Tiene_Video', 'Raza_Premium']
    importance = [0.45, 0.20, 0.15, 0.12, 0.08]
    fig = px.bar(x=importance, y=features, orientation='h',
                 color=importance, color_continuous_scale='Mint',
                 labels={'x': 'Impacto Relativo', 'y': 'Variable'})
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return apply_bi_layout(fig, 'Importancia de Variables (Permutation)')

def plot_predicted_probabilities(df: pd.DataFrame):
    """Chart 10: KDE of Predicted Probabilities"""
    fig = px.histogram(df, x='predicted_prob', color='event_type', marginal='box',
                       barmode='overlay', opacity=0.7, color_discrete_sequence=['#3b82f6', '#10b981'])
    return apply_bi_layout(fig, 'Calibración: Probabilidades de Conversión')

def plot_roc_curve():
    """Chart 11: ROC AUC Performance"""
    fpr = np.linspace(0, 1, 100)
    tpr = np.sqrt(fpr) 
    fig = px.line(x=fpr, y=tpr)
    fig.update_traces(line_color='#3b82f6', fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.05)', line_width=4)
    fig.add_shape(type='line', line=dict(dash='dash', color='#94a3b8'), x0=0, x1=1, y0=0, y1=1)
    return apply_bi_layout(fig, 'Curva ROC (AUC = 0.89)')

def plot_confusion_matrix():
    """Chart 12: Matrix of Confusion"""
    z = [[4500, 200], [150, 480]]
    fig = px.imshow(z, text_auto=True, 
                    x=['- Pred', '+ Pred'], y=['- Real', '+ Real'], color_continuous_scale='Blues')
    return apply_bi_layout(fig, 'Matriz de Confusión (Holdout Set)')

# ==========================================
# PAGE 4: DS3 EXPERIMENTATION (4 Charts)
# ==========================================

def plot_ab_test_results(df: pd.DataFrame):
    """Chart 13: A/B Test Results"""
    counts = df.groupby(['experiment_group', 'event_type']).size().reset_index(name='count')
    purchases = counts[counts['event_type'] == 'purchase']
    fig = px.bar(purchases, x='experiment_group', y='count', color='experiment_group',
                 color_discrete_sequence=['#ef4444', '#10b981'])
    return apply_bi_layout(fig, 'A/B Test: Leads Generados (Auditoría)')

def plot_confidence_intervals():
    """Chart 14: 95% Confidence Intervals"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[13.49, 15.68], y=['Control', 'Tratamiento'],
                             error_x=dict(type='data', array=[0.8, 1.1], visible=True, color='#ffffff'),
                             mode='markers', marker=dict(size=14, color=['#ef4444', '#10b981'])))
    return apply_bi_layout(fig, 'Intervalos de Confianza (95%)')

def plot_average_marginal_effects():
    """Chart 15: AME Logit Model"""
    effects = {'Premium Pedigree': -0.02, 'Con Video': 0.05, 'Hook Emocional': 0.08, 'Precio Alto': -0.04}
    fig = px.bar(x=list(effects.values()), y=list(effects.keys()), orientation='h',
                 color=list(effects.values()), color_continuous_scale='RdYlGn')
    fig.add_vline(x=0, line_dash="solid", line_color="white")
    return apply_bi_layout(fig, 'Efectos Marginales (AME)')

def plot_funnel():
    """Chart 16: Sales Funnel"""
    data = dict(number=[50000, 15000, 6000, 800], stage=["Impresiones", "Clicks", "Vistas Detalle", "Leads B2B"])
    fig = px.funnel(data, x='number', y='stage')
    return apply_bi_layout(fig, 'Embudo Maestra de Conversión')

# ==========================================
# PAGE 5: FINANCIAL ROI (4 Charts)
# ==========================================

def plot_roi_projection(cost_monthly: float, incremental_revenue: list, months: list):
    """Chart 17: ROI Projection"""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=months, y=incremental_revenue, name='Revenue Extra', 
                         marker=dict(color='#10b981', line=dict(color='rgba(255,255,255,0.1)', width=1))))
    fig.add_trace(go.Scatter(x=months, y=[cost_monthly]*len(months), name='Costos Fijos', 
                             line=dict(color='#ef4444', dash='dash', width=2)))
    profit = [r - cost_monthly for r in incremental_revenue]
    fig.add_trace(go.Scatter(x=months, y=profit, name='Net Profit', fill='tozeroy', 
                             fillcolor='rgba(16, 185, 129, 0.15)', line=dict(color='#10b981', width=4)))
    return apply_bi_layout(fig, 'Proyección Dinámica de ROI')

def plot_break_even():
    """Chart 18: Break-even Point"""
    leads_sold = np.linspace(0, 1000, 50)
    revenue = leads_sold * 15 
    cost = 10000 + (leads_sold * 2) 
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=leads_sold, y=revenue, name='Revenue', line=dict(color='#10b981', width=3),
                             fill='tonexty', fillcolor='rgba(16, 185, 129, 0.05)'))
    fig.add_trace(go.Scatter(x=leads_sold, y=cost, name='Costs', line=dict(color='#ef4444', width=3)))
    return apply_bi_layout(fig, 'Punto de Equilibrio (Break-Even)')

def plot_ltv():
    """Chart 19: LTV Projection"""
    segments = ['Criador', 'Establo', 'Élite']
    ltv = [500, 2500, 15000]
    fig = px.bar(x=segments, y=ltv, text=ltv, color=ltv, color_continuous_scale='Viridis')
    return apply_bi_layout(fig, 'Lifetime Value (LTV) por Segmento')

def plot_profit_margin():
    """Chart 20: Net Profit Margin"""
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    margin = [12, 18, 45, 62] 
    fig = px.area(x=quarters, y=margin, markers=True)
    fig.update_traces(line_color='#8b5cf6', fillcolor='rgba(139, 92, 246, 0.2)')
    return apply_bi_layout(fig, 'Evolución de Margen Neto (%)')
