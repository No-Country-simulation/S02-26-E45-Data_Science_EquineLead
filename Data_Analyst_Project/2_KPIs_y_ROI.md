# Análisis de KPIs y Retorno de Inversión (ROI)

Este documento proyecta financieramente cómo el desarrollo técnico dentro del repositorio (Scraping, Modelos, A/B Tests) se traduce en dinero tangible para el negocio.

## 1. Definición de KPIs y Lógica 

Para monitorear el negocio de EquineLead, la lógica de negocio debe centrarse en los siguientes KPIs:

| KPI | Definición | Benchmark (Antes) | Target (Con EquineLead) |
| --- | --- | --- | --- |
| **Conversion Rate (CR)** | Porcentaje del tráfico mensual que interactúa y se convierte en lead calificado. | 13.5% | > 15.6% |
| **Costo por Lead (CPL)** | Costo total de infraestructura de DS/DE dividido en los nuevos leads generados. | \$N/A | < \$5 USD |
| **Ingreso por Lead (RPL)** | Lo que EquineLead le cobra al criador/vendedor por enviarle ese cliente potencial. | \$0 | \$15 USD |

## 2. Escenarios y Supuestos Financieros (ROI)

Fijamos un marco de proyección mensual con los hallazgos validados de tráfico y mejora algorítmica:

1. **Escenario Base (Base de Usuarios):** 200,000 visitas/sesiones mensuales.
2. **Impacto de Modelos + A/B Testing:** El equipo de desarrollo logró subir la conversión un ~2.1% absoluto neto (= ~4,200 leads mensuales adicionales que la plataforma estática no habría capturado).
3. **Valor Financiero Logrado:** Asumiendo un RPL de \$15 USD, son `4,200 leads x $15 = $63,000 USD` adicionales en revenue bruto por mes de la plataforma.
4. **Costo de Servidores y Squad de Datos:** Supongamos un CAC + Mantenimiento de modelos en la nube de \$10,000 USD/mes.

## 3. Fórmula y Cálculo Final del ROI

El ROI se usará para vender el impacto del proyecto a potenciales inversores o stakeholders del portal. Aplicamos la fórmula del ROI mensual:

$$ ROI = \frac{Retorno\:Adicional - Costo\:de\:Infraestructura}{Costo\:de\:Infraestructura} \times 100 $$

$$ ROI = \frac{\$63,000 - \$10,000}{\$10,000} \times 100 = \textbf{+530\%} $$

> **Interpretación Ejecutiva del ROI:** 
> La solución de datos diseñada por el equipo técnico ofrece un ROI directo del 530%. Es decir, el producto no es un gasto en "mejores algoritmos"; es una máquina de retorno de \~5.3x. La escalabilidad es absoluta ya que el costo computacional no sube al mismo ritmo que la capacidad de clasificar nuevos leads en tiempo real con la integración de APIs y el nuevo stack de desarrollo.
