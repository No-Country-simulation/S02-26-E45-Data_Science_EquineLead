import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_charts():
    # Set style
    plt.style.use('dark_background')
    sns.set_palette("husl")
    
    # 1. Gráfico de Impacto en Conversión (A/B Test Results)
    fig, ax = plt.subplots(figsize=(8, 6))
    
    categories = ['Antes\n(Directorio Estático)', 'Después\n(Algoritmo + Hook)']
    conversion_rates = [13.49, 15.68]
    colors = ['#ff6b6b', '#4ecdc4']
    
    bars = ax.bar(categories, conversion_rates, color=colors, width=0.5)
    
    # Add labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
    ax.set_ylabel('Tasa de Conversión (Leads/Tráfico) %')
    ax.set_title('Impacto en Generación de Leads (Crecimiento Relativo: +16.2%)', pad=20, fontsize=14, fontweight='bold')
    ax.set_ylim(0, 20)
    
    plt.tight_layout()
    plt.savefig('conversion_impact.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Gráfico de Proyección de ROI y Revenue
    fig, ax2 = plt.subplots(figsize=(10, 6))
    
    months = ['Mes 1', 'Mes 2', 'Mes 3', 'Mes 4', 'Mes 5', 'Mes 6']
    cost_monthly = np.array([10000] * 6)
    
    # Empezamos con el revenue base y va subiendo la captación
    base_revenue = 400000 # asumiendo 27k leads a $15 
    incremental_revenue = np.array([30000, 45000, 63000, 66000, 70000, 75000]) # Ramp-up de leads capturados
    total_net_profit = incremental_revenue - cost_monthly
    
    ax2.plot(months, incremental_revenue, marker='o', linewidth=3, label='Retorno Bruto Incremental (USD)', color='#feca57')
    ax2.plot(months, cost_monthly, marker='s', linestyle='--', linewidth=2, label='Costo Operativo Datos/ML (USD)', color='#ff6b6b')
    ax2.bar(months, total_net_profit, alpha=0.3, color='#1dd1a1', label='Ganancia Neta (ROI acumulado)')
    
    for i, v in enumerate(total_net_profit):
        ax2.text(i, v / 2, f'+${v/1000:.0f}k', ha='center', va='center', fontweight='bold', color='white')
        
    ax2.set_title('Proyección de ROI Económico (6 Meses)', fontsize=14, fontweight='bold', pad=20)
    ax2.set_ylabel('USD')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.2)
    
    plt.tight_layout()
    plt.savefig('roi_projection.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("Gráficos generados exitosamente: 'conversion_impact.png' y 'roi_projection.png'")

if __name__ == '__main__':
    generate_charts()
