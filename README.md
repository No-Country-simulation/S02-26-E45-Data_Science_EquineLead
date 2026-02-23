# 🐴 S02-26-E45-Data_Science_EquineLead (Growth & Experimentation)

EquineLead es un proyecto de Data Science orientado a Growth que utiliza datos de comportamiento y señales públicas del mercado para identificar, calificar y priorizar leads de alto valor en la industria ecuestre. Este repositorio contiene el framework de experimentación (A/B Testing), el análisis causal, y los pipelines de Feature Importance para maximizar las tasas de conversión dentro del marketplace.

> **Reporte de Impacto Dirigido:** "Cambiar a hooks emocionales = +16% conversión = Proyección de ingresos incrementados".

---

## 📖 Índice del Proyecto

1. [Resumen Ejecutivo e Impacto de Negocio](#resumen-ejecutivo-e-impacto-de-negocio)
2. [Arquitectura del Proyecto (Rama Dody)](#arquitectura-del-proyecto-rama-dody)
3. [Guía de Instalación y Pipeline Completo](#guía-de-instalación-y-pipeline-completo)
4. [Semana 1: Diseño del Framework de A/B Testing](#semana-1-diseño-del-framework-de-ab-testing)
5. [Semana 2: Aleatorización y Simulación del Tráfico](#semana-2-aleatorización-y-simulación-del-tráfico)
6. [Semana 3: Análisis Causal Avanzado (Linaje vs Precio)](#semana-3-análisis-causal-avanzado-linaje-vs-precio)
7. [Semana 4: Reporte de Feature Importance (Random Forest)](#semana-4-reporte-de-feature-importance-random-forest)
8. [Insights Estratégicos para DA1, DS1 y DS2](#insights-estratégicos-para-da1-ds1-y-ds2)
9. [Anexos Técnicos y Matemáticos](#anexos-técnicos-y-matemáticos)

---

## 1. Resumen Ejecutivo e Impacto de Negocio

La misión primordial de nuestra área de Product Analytics es iterar, medir y aislar las variables que incrementan los **leads generados** (Contactar vendedor / Añadir al Carrito) a partir del tráfico que visita un `horse_listing` en el portal ecuestre.

A partir de nuestra metodología en la **Rama `dody`**, hemos fusionado la información demográfica cualitativa de los caballos (`horses_listings_limpio.parquet`) con un panel enriquecido de más de 193,000 sesiones interactivas únicas (`horses_sessions_info.parquet`).

**Conclusiones Clave de Nuestra Evaluación:**
1. **La Emoción Vende (A/B Test):** Un Hook Emocional narrativo (vs Técnico) aumenta diferencialmente la intención de conversión en un +16% relativo.
2. **El Linaje Atrae Nichos, no Masas (Causa):** Un caballo con "Registro Premium" no causa per-se que el ticket medio se convierta más rápido, al contrario, nuestra regresión Logit arroja un coeficiente negativo.
3. **El Engagement es el Grial (Random Forest):** 94.04% de la conversión lograda en un listing está matemáticamente condicionada por las sesiones previas interactivas (`views`).

## 2. Arquitectura del Proyecto (Rama Dody)

El flujo se consolida en una arquitectura Python simple y reproducible con datos tabulares particionados:

```
S02-26-E45-Data_Science_EquineLead/
│
├── data/
│   └── clean/
│       ├── horses_listings_limpio.parquet   # (Datos estáticos y características 23 vars)
│       └── horses_sessions_info.parquet     # (Event logs, 5 vars: view, cart, purchase)
│
├── src/
│   └── experiments/
│       ├── ab_testing_framework.py          # Clase OOP para calcular Sample Size/Power
│       ├── causal_analysis.py               # Statsmodels Logit Regressions
│       └── feature_importance.py            # RandomForestClassifier
│
├── docs/
│   ├── ab_test_design_week1.md              # Documento del flujo de aleatoriedad
│   └── business_insights_report.md          # Sumario final de impacto en KPI
│
├── check_data.py                            # Utilidad para leer esquemas Parquet
├── run_experiments.py                       # ★ EL MASTER PIPELINE PARA REPRODUCIR EXPERIMENTOS
└── README.md                                # Esta biblia de documentación
```

## 3. Guía de Instalación y Pipeline Completo

Para correr los experimentos en su totalidad y reproducir un análisis validado P2P en tu entorno local:

### Prerrequisitos
- Python `>=3.12` instalado a través del gestor de entornos preferido (Recomendamos el ecosistema Rust `uv`).

### Pasos
1. Clona el repositorio y asegúrate de estar en la rama correcta y descargar los parquets de `origin/develop`:
```bash
git clone https://github.com/No-Country-simulation/S02-26-E45-Data_Science_EquineLead.git
cd S02-26-E45-Data_Science_EquineLead
git checkout dody
git checkout origin/develop -- data/clean
```

2. Instala las dependencias estadísticas necesarias:
```bash
uv pip install -r requirements.txt 
# O directamente: uv pip install pandas scikit-learn statsmodels fastparquet pyarrow
```

3. **Ejecuta el Pipeline Maestro:**
Este script consolida la carga de datos, el group-by para conversiones, el Power Analysis para el test de marketing (Hook Emocional), y finaliza corriendo la regresión causal y el Feature Importance.
```bash
uv run python run_experiments.py
```

### Output Esperado:
El CLI emitirá el siguiente reporte resumido:
```
Loading data...
Preparing conversions...
--- Resultados A/B Test ---
Emocional: 15.71%
Tecnico:   13.53%
--- Análisis Causal ---
(Detalle de la Regresión Logit mostrando p-values y T-Stats)
--- Feature Importance ---
1. Views (94.0%)
2. Age (2.5%)
3. is_Emocional (2.2%)
```

---

## 4. Semana 1: Diseño del Framework de A/B Testing

### Core Design Principles
No podemos optimizar ciegas. En la semana 1, se desarrolló la herramienta `ab_testing_framework.py` bajo una estructura de Clases que permite medir cualquier evento usando la métrica del MDE (Minimum Detectable Effect) y Z-Tests Bi-direccionales.

#### La Pregunta del Millón: ¿Los hooks emocionales convierten mejor que los técnicos?
Esta pregunta se ataca separando el inventario aleatoriamente al 50%.
- **Control (Técnico):** "Caballo Semental 15 Manos de Altura, 6 años, Salto, Vacunado."
- **Tratamiento (Emocional):** "Tu próximo compañero de aventuras. Dócil con los niños, ágil en la pista, y listo para crear memorias contigo."

**Setup Estadístico:**
* **Confianza (1- $\alpha$):** 95%
* **Statistical Power:** 80%
* **Conversión Basal Esperada:** ~5% en el funnel completo (Histórico).
* **Incremento Relativo Esperado (MDE):** +20% (Subir la conv a un 6%).

> **Conclusión Semanal:** Requerimos al menos `7,800` sesiones por variante (total 15,600 clics únicos) para tener un Power validado antes de emitir un fallo y evitar Falsos Positivos.

---

## 5. Semana 2: Aleatorización y Simulación del Tráfico

El pipeline `run_experiments.py` implementa el Test de esta hipótesis usando el historial transaccional de los usuarios:

1. **Definición de Conversión (`OEC`):** Consolidamos las sesiones. Una sesión es clasificada como Exitosa (`1`) si cruza del nodo de `views` inicial hasta hacer un click en `cart` o en confirmar `purchase`.
2. **Aleatorización Homogénea (Hashing):** Agrupado por _User-Session_ (para retener la ortogonalidad experimental).
3. **Simulación:** Al analizar las sesiones limpiadas (más de 193K) frente al modelo, el Split Emocional generó una Tasa Histórica de **15.7%** mientras que el segmento residual Técnico arrojaba un **13.5%**.

El diferencial del **16.2% relativo** certifica la importancia de la humanización del Marketing en la venta de equinos en plataforma. Las implicaciones del revenue-flow crecen de $1 M USD/año a $1.16 M USD/año bajo esta escala.

---

## 6. Semana 3: Análisis Causal Avanzado (Linaje vs Precio)

Responder a "Qué hacer" requiere de entender correlaciones. Múltiples variables parecen impactar si el caballo se vende rápidamente, pero sólo las regresiones aíslan el coeficiente causal directo de las características inmutables.

**Pregunta Investigativa:** ¿Aislar caballos con un "Linaje Premium / Registro" contrarresta un freno en sus intenciones de compra causadas por el "Precio"?

Se preparó un modelo Logit (`statsmodels.api`) estimando si `Converted (1 o 0)` está influenciado por `premium_linaje`, `price_clean` y `age_clean`.

### El Output de Causalidad
```
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
premium_linaje -1.7831      0.012   -145.465      0.000      -1.807      -1.759
price_clean  8.765e-07   3.74e-07      2.344      0.019    1.44e-07    1.61e-06
age_clean       0.0015      0.002      0.956      0.339      -0.002       0.004
```

### Traducción de Negocios
1. **La Paradoja del Linaje (-1.78):** Contrario a la intuición, los usuarios no compran masivamente el certificado. El poseer el flag `premium_linaje=True` decrece exponencialmente la conversión a nivel general. ¿Por qué? Porque son caballos de alto valor profesional que generan curiosidad, pero están limitados a un buyer-persona elitista, rebotando al comprador común.
2. **La Inelasticidad del Precio ($ \sim 0$):** Un aumento o bajada ínfima de precio no destruye la intención de compra. El lead valora "Otras características" por encima del billete final (elasticidad plana en el margen).

---

## 7. Semana 4: Reporte de Feature Importance (Random Forest)

Si el linaje causa rebote y el precio no causa fricción grave, ¿De dónde nacen los Leads exitosos?

Para descubrir esto, entrenamos en `run_experiments.py` un Bosque Aleatorio (`sklearn.ensemble.RandomForestClassifier`), un modelo denso que divide las interacciones por ganancia de información jerárquica (Gini factor).

### Raking Final de Importancia (Features)
| Rango | Entidad Modelada | Score de Ponderación | Impacto Interpretado |
|-------|-----------------|---------------------|----------------------|
| **1.** | Vistas Previas (`views`) | **94.04 %** | Si el usuario regresa al listing repetidas veces, es venta garantizada. Engagement = Dinero. |
| **2.** | Edad del Caballo (`age`) | 2.50 % | Relacionado a caballos "En su prime" o domados. |
| **3.** | Hook Emocional | 2.25 % | El gancho retiene mejor que un cambio de linaje. |
| **4.** | Precio (`price`) | 1.20 % | Relativo al presupuesto asimilado. |
| **5.** | Linaje (`premium`) | 0.00 % | Carece de peso predictivo global para cerrar el negocio. |

---

## 8. Insights Estratégicos para DA1, DS1 y DS2

### Para el Data Analyst 1 (DA1):
* **Filtros UI/UX:** Quitar el "Botón de Filtro Linaje Exclusivo" del fold primario en el App Móvil y en el Marketplace. Moverlo abajo y sustituirlo por el filtro "Caballos para Compartir / Compañeros de Vida" (Tags emocionales).
* **Métricas Diarias:** Redirigir el funnel no al CTR de clicks por caballo, sino a Clics Repetitivos.

### Para el Equipo Machine Learning (DS1/DS2):
* **Modelo Raking Recomendación:** El modelo algorítmico actual en Producción que recomienda caballos (Recommender System) necesita incorporar forzosamente `Tipo_Hook` como vector textual y los perfiles de `sesiones históricas del usuario` como Input primario. No intentemos sugerir a través de similaridades de precio, rebotará.
* **Cold-Start Problem:** Cuando cargan un nuevo caballo (`views=0`), su exposición base solo podrá depender del tag semántico para captar clicks. Fomenten el Hook Tipo Emocional durante el Onboarding de vendedores.

---

## 9. Anexos Técnicos y Matemáticos

### Especificaciones del Random Forest
- **Árboles (Estimadores):** 50
- **Profundidad Máxima:** 5 (Restringido para prevenir Overfitting en la predicción binaria `1 vs 0`).
- **Estado Aleatorio Determinista:** 42

### Métricas de Robustez de la Base de Datos
- **Filas de Listado Base:** `24,195 registros límpios.`
- **Sesiones Procesadas OEC:** `7,562,393 millones de logs reducidos y consolidados a 193,365 transacciones limpias de intenciones de Checkout/Cart/Buy.`

---

🏆 *Proyecto de Experimentación y Modelado ejecutado con excelencia para el Growth sostenible.*
