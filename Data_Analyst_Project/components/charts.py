import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_roi_projection(cost_monthly: float, incremental_revenue: list, months: list):
    \"\"\"Plots the ROI Projection\"\"\"
    fig, ax2 = plt.subplots(figsize=(10, 6))
    plt.style.use('dark_background')
    
    cost_array = np.array([cost_monthly] * len(months))
    incremental_array = np.array(incremental_revenue)
    total_net_profit = incremental_array - cost_array
    
    ax2.plot(months, incremental_array, marker='o', linewidth=3, label='Retorno Bruto Incremental (USD)', color='#feca57')
    ax2.plot(months, cost_array, marker='s', linestyle='--', linewidth=2, label='Costo Operativo ML (USD)', color='#ff6b6b')
    ax2.bar(months, total_net_profit, alpha=0.3, color='#1dd1a1', label='Ganancia Neta (ROI acumulado)')
    
    for i, v in enumerate(total_net_profit):
        ax2.text(i, v / 2, f'+${v/1000:.0f}k', ha='center', va='center', fontweight='bold', color='white')
        
    ax2.set_title('Proyección de ROI Económico (6 Meses)', fontsize=14, fontweight='bold', pad=20)
    ax2.set_ylabel('USD')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.2)
    return fig

def plot_conversion_impact(conv_base: float, conv_optimizada: float):
    \"\"\"Plots A/B Test Results\"\"\"
    fig, ax = plt.subplots(figsize=(8, 6))
    plt.style.use('dark_background')
    
    categories = ['Antes\n(Estático)', 'Después\n(Algoritmo)']
    conversion_rates = [conv_base, conv_optimizada]
    colors = ['#ff6b6b', '#4ecdc4']
    
    bars = ax.bar(categories, conversion_rates, color=colors, width=0.5)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), 
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
    ax.set_ylabel('Tasa de Conversión %')
    ax.set_title('Impacto en Generación de Leads', pad=20, fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(conversion_rates) + 5)
    return fig
