import streamlit as st
from components.ui_cards import render_alert

st.set_page_config(page_title="Executive Pitch", page_icon="🎯")

st.header("4. El Pitch Final (Alineación Ejecutiva)")
st.markdown("### EquineLead: La Máquina de Monetizar Datos")

st.markdown("""
**1. Dónde estábamos (El Problema):**
Una plataforma estática con una tasa baja y estancada de contactos (~13%). La información de calidad premium competía ineficazmente con caballos recreacionales por falta de filtros algorítmicos.

**2. La Evolución (Nuestra Solución Tecnológica):**
*   **Data Engineering:** Reemplazó el proceso manual y ahora captura el pulso del mercado real 24/7 sin fallos (Scrapers robustos).
*   **Machine Learning (DS1/MLE):** Modeló características predictivas y creó *Recomendaciones Dinámicas*, logrando empaquetar estos insights en un dashboard/API escalable.
*   **Experimentación (DS3):** Sometió intuiciones al rigor empírico. Encontramos que un *Hook Emocional* incrementa masivamente el contacto en nuestro canal masivo, y validamos que el comportamiento pasado (vistas) es el rey sobre atributos estáticos como el precio.

**3. El Impacto Económico (Resultados Data Analyst):**
Ajustar estos engranajes aumentó de inmediato el embudo central en un **+16% relativo (Uplift absoluto de >2% general)**. En términos monetizados (vendiendo visibilidad calificada B2B), justifica por sí solo el costo de infraestructura (Nube, APIs) y del equipo completo de datos de la compañía, entregando un ROI superior al **530%** al mes asumiendo 200,000 interacciones basales.

**Conclusión:**
EquineLead dejó de ser un sitio web corporativo de listados. Ahora es un sistema de predicción financiera validado empíricamente, escalable, y lo más importante: **altamente rentable**.
""")

render_alert("¡Pitch Ejecutivo completado con éxito y listo para la presentación al Board de Inversores! ✅", type="success")
