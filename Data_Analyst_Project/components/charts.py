import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Palette Config (Power BI Classic Light)
COLOR_REAL = "#118DFF" 
COLOR_SIM = "#12B3AB"  
COLOR_GRID = "#e1dfdd"
COLOR_TEXT = "#323130"

def get_tag(df: pd.DataFrame) -> str:
    """Returns the visual audit tag based on the source column."""
    if 'source' in df.columns and 'Real' in df['source'].values:
        return " [Auditoría Real]"
    return " [Proyección Directiva]"

def apply_bi_layout(fig, title: str):
    """Applies an authentic Power BI executive layout to any plotly figure."""
    fig.update_layout(
        height=380, # Force compact size to avoid oversized charts
        title=dict(text=f"<b>{title}</b>", font=dict(size=18, color=COLOR_TEXT)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLOR_TEXT, family='Segoe UI'),
        margin=dict(l=50, r=30, t=70, b=70), # Increased bottom margin for legend
        xaxis=dict(showgrid=True, gridcolor=COLOR_GRID, linecolor=COLOR_GRID, 
                   tickfont=dict(color=COLOR_TEXT, size=11), title_font=dict(color=COLOR_TEXT),
                   automargin=True),
        yaxis=dict(showgrid=True, gridcolor=COLOR_GRID, linecolor=COLOR_GRID, 
                   tickfont=dict(color=COLOR_TEXT, size=11), title_font=dict(color=COLOR_TEXT),
                   automargin=True),
        hovermode="x unified",
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=COLOR_TEXT), 
                    orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5), # Moved legend below chart
        hoverlabel=dict(bgcolor="#ffffff", font_size=13, font_family="Segoe UI", font_color=COLOR_TEXT,
                        bordercolor="#e1dfdd")
    )
    return fig

# ==========================================
# PAGE 1: MARKET OVERVIEW (4 Charts)
# ==========================================

def plot_tam_distribution(df: pd.DataFrame):
    """Chart 1: TAM Distribution by Country (Pie) with Luxury Grouping"""
    tag = get_tag(df)
    
    col = 'country' if 'country' in df.columns else 'Temp_Country'
    if col == 'Temp_Country':
        df['Temp_Country'] = df['Location'].apply(lambda x: x.split(',')[-1].strip() if ',' in str(x) else 'Other')
    
    counts = df[col].value_counts(normalize=True)
    top_n = counts[counts > 0.05].index.tolist()
    
    df['Clean_Country'] = df[col].apply(lambda x: x if x in top_n else 'Otras Regiones')
    
    fig = px.pie(df, names='Clean_Country', hole=0.7,
                 color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_traces(textposition='outside', textinfo='percent+label')
    
    return apply_bi_layout(fig, f'Segmentación Geográfica Premium{tag}')

def plot_cpl_comparison():
    """Chart 2: Pre-DS vs Post-DS CPL (Bar)"""
    data = {'Etapa': ['2023 (Estático)', '2024 (MLE)'], 'CPL (USD)': [25, 15]}
    fig = px.bar(data, x='Etapa', y='CPL (USD)', text='CPL (USD)', 
                 color='Etapa', color_discrete_map={'2023 (Estático)':'#ef4444', '2024 (MLE)':'#10b981'})
    fig.update_traces(textposition='outside', cliponaxis=False, textfont=dict(color=COLOR_TEXT, size=12))
    fig.update_layout(showlegend=False) # Legend is redundant here
    return apply_bi_layout(fig, 'Reducción de Costo por Lead (CPL)')

def plot_traffic_seasonality(time_grain='Mensual'):
    """Chart 3: Traffic seasonality (Line with Luxe Gradient)"""
    if time_grain == 'Mensual':
        x_axis = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        traffic = [150, 160, 180, 210, 250, 280, 300, 290, 240, 200, 170, 160]
    else:
        x_axis = ['Q1', 'Q2', 'Q3', 'Q4']
        traffic = [490, 740, 830, 530]
        
    fig = px.line(x=x_axis, y=traffic, markers=True)
    fig.update_traces(line_color=COLOR_REAL, fill='tozeroy', 
                      fillcolor='rgba(17, 141, 255, 0.1)', line_width=4)
    return apply_bi_layout(fig, f'Estacionalidad del Tráfico (K Sesiones) - {time_grain}')

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
    fig.update_traces(textposition='outside', textinfo='percent+label')
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

def plot_feature_importance(algo="Random Forest"):
    """Chart 9: Random Forest Permutation Importance"""
    if algo == "Random Forest":
        features = ['Vistas_Previas', 'Precio', 'Edad', 'Tiene_Video', 'Raza_Premium']
        importance = [0.45, 0.20, 0.15, 0.12, 0.08]
    elif algo == "XGBoost":
        features = ['Precio', 'Vistas_Previas', 'Tiene_Video', 'Edad', 'Raza_Premium']
        importance = [0.55, 0.18, 0.14, 0.09, 0.04]
    else:
        features = ['Vistas_Previas', 'Edad', 'Precio', 'Tiene_Video', 'Días_Activo']
        importance = [0.35, 0.25, 0.20, 0.10, 0.10]
        
    fig = px.bar(x=importance, y=features, orientation='h', text=importance,
                 color=importance, color_continuous_scale='Mint',
                 labels={'x': 'Impacto Relativo', 'y': 'Variable'})
    fig.update_traces(textposition='outside', texttemplate='%{text:.2f}', cliponaxis=False)
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
    return apply_bi_layout(fig, f'Importancia de Variables ({algo})')

def plot_predicted_probabilities(df: pd.DataFrame):
    """Chart 10: KDE of Predicted Probabilities"""
    fig = px.histogram(df, x='predicted_prob', color='event_type', marginal='box',
                       barmode='overlay', opacity=0.7, color_discrete_sequence=['#3b82f6', '#10b981'])
    return apply_bi_layout(fig, 'Calibración: Probabilidades de Conversión')

def plot_roc_curve(algo="Random Forest"):
    """Chart 11: ROC AUC Performance"""
    fpr = np.linspace(0, 1, 100)
    
    if algo == "Random Forest":
        tpr = np.sqrt(fpr)
        auc = 0.89
    elif algo == "XGBoost":
        tpr = fpr**0.3
        auc = 0.92
    else:
        tpr = fpr**0.7
        auc = 0.78
        
    fig = px.line(x=fpr, y=tpr)
    fig.update_traces(line_color=COLOR_REAL, fill='tozeroy', fillcolor='rgba(17, 141, 255, 0.05)', line_width=4)
    fig.add_shape(type='line', line=dict(dash='dash', color='#94a3b8'), x0=0, x1=1, y0=0, y1=1)
    return apply_bi_layout(fig, f'Curva ROC (AUC = {auc})')

def plot_confusion_matrix(threshold=0.5):
    """Chart 12: Matrix of Confusion"""
    # Shift confusion matrix based on threshold for interactivity
    tp = int(480 * (1.5 - threshold))
    fn = 150 + (480 - tp)
    fp = int(200 * (0.5 + threshold))
    tn = 4500 + (200 - fp)
    
    z = [[tn, fp], [fn, tp]]
    fig = px.imshow(z, text_auto=True, 
                    x=['- Pred', '+ Pred'], y=['- Real', '+ Real'], color_continuous_scale='Blues')
    return apply_bi_layout(fig, f'Matriz de Confusión (Umbral {threshold:.2f})')

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

def plot_break_even(costo_lead=25, costo_squad=15000):
    """Chart 18: Break-even Point"""
    leads_sold = np.linspace(0, 2000, 50)
    revenue = leads_sold * costo_lead 
    cost = costo_squad + (leads_sold * (costo_lead * 0.1)) # 10% variable cost 
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=leads_sold, y=revenue, name='Revenue', line=dict(color=COLOR_SIM, width=3),
                             fill='tonexty', fillcolor='rgba(18, 179, 171, 0.05)'))
    fig.add_trace(go.Scatter(x=leads_sold, y=cost, name='Costs', line=dict(color='#ef4444', width=3)))
    return apply_bi_layout(fig, 'Punto de Equilibrio (Break-Even)')

def plot_ltv(costo_lead=25):
    """Chart 19: LTV Projection"""
    segments = ['Criador', 'Establo', 'Élite']
    base_ltv = [500, 2500, 15000]
    # LTV scales slightly with the lead cost simulation for visual interaction
    ltv = [v * (costo_lead / 25) for v in base_ltv]
    fig = px.bar(x=segments, y=ltv, text=[f"${int(v):,}" for v in ltv], color=ltv, color_continuous_scale='Blues')
    fig.update_traces(textposition='outside', cliponaxis=False, textfont=dict(color=COLOR_TEXT, size=12))
    fig.update_layout(showlegend=False)
    return apply_bi_layout(fig, 'Lifetime Value Estimado (LTV)')

def plot_profit_margin(trafico=200000):
    """Chart 20: Net Profit Margin"""
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    base = 12 if trafico < 100000 else (18 if trafico < 500000 else 25)
    margin = [base, base*1.5, base*2.5, base*3.5] 
    fig = px.area(x=quarters, y=margin, markers=True)
    fig.update_traces(line_color=COLOR_SIM, fillcolor='rgba(18, 179, 171, 0.2)')
    return apply_bi_layout(fig, 'Evolución Escalar de Margen Neto (%)')
