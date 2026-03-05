# Documentación Técnica — Modelo de Lead Scoring
### Proyecto EquineLead · Data Science Team

---

## Índice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Descripción del problema y definición de targets](#2-descripción-del-problema-y-definición-de-targets)
3. [Fuentes de datos y estrategia de merge](#3-fuentes-de-datos-y-estrategia-de-merge)
4. [Limpieza y tratamiento de datos](#4-limpieza-y-tratamiento-de-datos)
5. [Feature Engineering](#5-feature-engineering)
6. [Observaciones relevantes del EDA](#6-observaciones-relevantes-del-eda)
7. [Preprocesamiento para el modelado](#7-preprocesamiento-para-el-modelado)
8. [Arquitectura del modelo: clasificación en cascada](#8-arquitectura-del-modelo-clasificación-en-cascada)
9. [Experimentos y resultados](#9-experimentos-y-resultados)
10. [Modelo campeón y feature selection](#10-modelo-campeón-y-feature-selection)
11. [Tracking con MLflow / DagsHub](#11-tracking-de-experimentos-con-mlflow--dagshub)
12. [Estructura del pipeline de producción](#12-estructura-del-pipeline-de-producción)
13. [Decisiones descartadas y su justificación](#13-decisiones-descartadas-y-su-justificación)

---

## 1. Resumen ejecutivo

El objetivo es clasificar a cada lead en tres niveles de valor:

| Nivel | Criterio |
|---|---|
| **Lead Bronce** | No realizó ninguna compra |
| **Lead Plata** | Compró caballos < USD 50.000 **o** productos < USD 2.000 |
| **Lead Oro** | Compró caballos ≥ USD 50.000 **o** productos ≥ USD 2.000 |

La clasificación se hace de forma **independiente para dos verticales**: `horse_target` y `prods_target`. El desafío principal es el desbalance extremo: Lead Oro representa menos del 1 % del total. El modelo campeón es **XGB Tuneado con feature selection por dominio**, logrando un **F2 Lead Oro horse ≈ 0.51** con gap de overfitting controlado (< 0.10).

En la segunda iteración (`LeadScoring_v2.ipynb`) se exploraron LightGBM con Optuna y CatBoost con categóricas nativas como alternativas al XGB campeón. Ninguno lo superó en F2 Lead Oro horse; el XGB Tuneado mantiene el título.

---

## 2. Descripción del problema y definición de targets

### Por qué dos targets separados

Un comprador de sillas de montar de alta gama no necesariamente compra caballos de competición, y viceversa. Tratar el problema con un único target multiclase ignoraría esta independencia y generaría predicciones menos accionables para los equipos de ventas. Dos targets permiten además priorizar leads de forma independiente según el área comercial.

### Umbrales de clasificación

Los umbrales (USD 50.000 para caballos, USD 2.000 para productos) representan percentiles altos del precio de compra observado, separando transacciones de bajo valor de transacciones donde el lead tiene poder adquisitivo real.

### Casos inconsistentes

Existen 1–2 filas donde un usuario es Lead Oro en caballos pero Lead Bronce en productos. Son anomalías en la definición del target (usuario que compró un caballo de alto valor pero nunca interactuó con productos). Se documentan pero no se eliminan antes del split.

---

## 3. Fuentes de datos y estrategia de merge

### Las 5 tablas originales

| Tabla | Contenido | Granularidad |
|---|---|---|
| `users_info` | Perfil del usuario: país, trabajo, email, tarjeta | 1 fila / usuario |
| `horses_listings_limpio` | Catálogo de caballos: raza, precio, skills, breed | 1 fila / caballo |
| `products_listing_limpio` | Catálogo de productos: descripción, precio, categoría | 1 fila / producto |
| `horses_sessions_info` | Eventos de sesión en caballos: view, cart, purchase | 1 fila / evento |
| `prods_sessions_info` | Eventos de sesión en productos: view, cart, purchase | 1 fila / evento |

### Estrategia de merge
```
horsesInfo  ──(horse_id = Horse_ID)──►  df_horses   ──(user_id)──►  df_horses + users
prodsInfo   ──(item_id  = Item_ID) ──►  df_products  ──(user_id)──►  df_products + users
```

Se enriquecen primero los eventos con los atributos del ítem (precio, raza, skills) y luego con el perfil del usuario, para poder agregarlos todos juntos en un solo `groupby` por `user_id`. Se usa **LEFT JOIN** para conservar todos los eventos incluso si el ítem fue eliminado del catálogo, evitando perder señal de comportamiento real.

### De eventos a usuarios

Los DataFrames de eventos tienen millones de filas; el modelo opera sobre una fila por usuario. Se genera una feature matrix agregada usando conteos, medias, máximos, proporciones y modas. Esta agregación es donde se produce la mayor parte de las features del modelo.

---

## 4. Limpieza y tratamiento de datos

### Nulos

- `horsesInfo.user_session` y `prodsInfo.user_session`: porcentaje ínfimo (< 0.1 %). Se eliminan las filas — no son sesiones reales identificables.
- El resto de nulos en `horses` y `products` (campos con valor `"unknown"`) se tratan como categoría informativa en la FE.

### Duplicados

Se detectaron y eliminaron duplicados en `horsesInfo` y `prodsInfo`. Origen probable: captura múltiple del mismo evento por el sistema de tracking.

### Conversiones de tipo

| Campo | Problema | Solución |
|---|---|---|
| `event_time` (sesiones) | String en lugar de datetime | `pd.to_datetime().dt.date` |
| `Temperament` (horses) | String numérico con valores no parseables | `pd.to_numeric(errors='coerce').astype('Int64')` |
| `first_seen` (users) | Datetime con timezone inconsistente | `tz_localize(None)` tras strip de tz |

### Columnas eliminadas

| Columna | Motivo |
|---|---|
| `name`, `addres`, `phone_number` (users) | PII sin valor predictivo |
| `email`, `credit_card_info`, `job_info` (users) | Se extrae la señal útil y se descarta el raw |
| `city` (users) | 800+ categorías sin ninguna dominante — Cramér's V < 0.02 |
| `Company Profile` (horses) | 85 % desconocidos; los conocidos son URLs inutilizables |
| `Images`, `URL` (products) | Sin señal |
| `Name`, `Last Update`, `Horse Profile` (horses) | Identificadores o texto libre sin estructura |

---

## 5. Feature Engineering

### Tabla `users`

**`prestige_score` (1–10):** se extrae el título del campo `job_info` y se asigna un score de prestigio económico estimado. La hipótesis es que inversores o CEOs tienen mayor probabilidad de ser Lead Oro.
```
10 → investor, family office, high-net-worth, bloodstock
 9 → olympic, FEI, grand prix, national team
 7 → owner, director, founder, CEO, manager
 5 → veterinarian, specialist, physiotherapist
 3 → resto
```

**`domain`:** proveedor de email (gmail, hotmail, yahoo, outlook, other/strange). Los dominios corporativos pueden correlacionar con perfiles profesionales.

**`card_issuer`:** emisor de tarjeta, extraído y normalizado (VISA/Visa/visa → VISA, bancos locales raros agrupados).

**`region`:** 69 países → 7 regiones geográficas. Reduce cardinalidad sin perder señal geográfica.

**`user_antiguedad_dias`:** días desde `first_seen` hasta el último evento registrado. Captura la madurez del usuario en la plataforma.

### Tabla `horses`

**`is_pro_seller`:** binaria, 1 si el vendedor tiene `Company Name` distinto de "unknown". Un comprador de caballos de vendedores profesionales tiene mayor poder adquisitivo.

**`color_grouped`:** 40+ valores → 10 grupos semánticos (bay_brown, grey_white, pinto_paints, etc.). Reduce cardinalidad manteniendo diferencias de mercado.

**`breed_family`:** razas → 8 familias (western_stock, sport_racing, baroque_iberian, gaited_horses, draft_heavy, ponies_minis, primitive_longears, other). Refleja el perfil del comprador.

**Skills → 5 features:** `is_sport_elite` (FEI/dressage/jumping), `is_working_elite` (reining/cutting/polo), `is_family_safe` (kid safe/beginner), `num_skills` (versatilidad), `tech_score` (score ponderado).

**`has_shipping`, `has_registry`, `has_markings`:** flags de formalidad del anuncio.

**`comment_word_count`:** más palabras en el anuncio sugiere un caballo de mayor valor y vendedor más elaborado.

### Tabla `products`

A partir del campo `Description` se extraen 8 features por producto: `brand`, `target_user`, `origin`, `is_waterproof`, `is_breathable`, `has_uv_protection`, `is_leather`, `machine_washable`. Las marcas se normalizan y las de < 10 apariciones se agrupan en `other_niche_brands`.

### Features derivadas (post-merge, por usuario)

| Feature | Fórmula | Qué captura |
|---|---|---|
| `ratio_cart_horse` | cart_adds / (views + 1) | Intención de compra en caballos |
| `ratio_cart_global` | total_cart / (total_views + 1) | Intención global |
| `rango_precio_horse` | max_price − min_price | Amplitud del rango de precios explorado |
| `prestige_gap` | prestige_horses − prestige_prods | Diferencia de perfil entre verticales |
| `ratio_recurrencia_horse` | views / (caballos_unicos + 1) | Patrón de revisita concentrada |
| `max_visitas_mismo_caballo` | max revisitas a un caballo individual | Interés concentrado = señal fuerte de intención |
| `has_both_interests` | (horse_views>0) & (prod_views>0) | Usuario activo en ambas verticales |

### Features nuevas exploradas en v2 (no incorporadas al campeón)

| Feature | Fórmula | Resultado |
|---|---|---|
| `precio_aspiracional_horse` | max_horse_price / (avg_horse_price + 1) | No mejoró sobre `max_horse_price_viewed`; señal redundante |
| `precio_aspiracional_prods` | max_product_price / (avg_product_price + 1) | Ídem dominio productos |

---

## 6. Observaciones relevantes del EDA

### Desbalance severo — el factor técnico principal
```
horse_target:   Bronce ~85 %  |  Plata ~14 %  |  Oro ~1 %
prods_target:   Bronce ~87 %  |  Plata ~12 %  |  Oro ~1 %
```

Este desbalance justifica la arquitectura en cascada, el uso de SMOTE/scale_pos_weight, F2-score como métrica y la decisión de no usar un clasificador multiclase directo.

### Features más discriminativas (bivariado)

Las variables con mayor separación entre clases según violinplots y KDE:

1. **`max_horse_price_viewed`** — el precio máximo que el usuario estuvo dispuesto a explorar es el predictor más fuerte de Lead Oro.
2. **`max_visitas_mismo_caballo`** — Lead Oro vuelve al mismo caballo varias veces antes de comprar (señal de evaluación profunda).
3. **`horses_added_to_cart`** — acción de alta intención de compra.
4. **`ratio_recurrencia_horse`** — revisita concentrada en pocos caballos.
5. **`avg_prestige_score_horses`** — promedio de prestige de los caballos vistos refleja el segmento de mercado explorado.
6. **`viewed_sport_elite`** — ver caballos FEI/dressage correlaciona fuertemente con Lead Oro.
7. **`user_prestige_score`** — perfil laboral del usuario aporta señal independiente del comportamiento.
8. **`user_antiguedad_dias`** — usuarios más antiguos tienen mayor probabilidad de haber completado una compra.

### Variables categóricas — baja señal cruda, señal no lineal real

El análisis de Cramér's V mostró coeficientes muy bajos (< 0.10) en todas las categóricas. Sin embargo, esto no implica que no tengan información — solo que la señal es no lineal. Por eso se optó por Target Encoding en lugar de eliminarlas.

> **Nota v2:** En el notebook `LeadScoring_v2.ipynb` las columnas categóricas se buscaron con nombres distintos (`gender_with_most_appearances`, `breedFamily_with_most_appearances`, `color_grouped_with_most_appearances`) que no existen en `df_final.parquet`. Los nombres correctos son `gender_mode`, `breed_family_mode` y `color_mode` tal como los genera el `groupby` en `features.py`. Corregir `CAT_COLS` en v2 antes de usar ese notebook.

### Colinealidad alta — documentada, no eliminada

Se identificaron 6 grupos con correlación > 0.77:

| Grupo | Variables | Correlación |
|---|---|---|
| Vistas globales | total_views, horses_viewed, products_viewed | 0.994–0.999 |
| Carritos | total_cart_adds, horses_added_to_cart, products_added_to_cart | 0.990–0.995 |
| Ratios de carrito | ratio_cart_horse, ratio_cart_prods, ratio_cart_global | 0.932–0.975 |
| Precios de caballos | max/avg/min_horse_price, rango_precio | 0.520–0.951 |
| Vistas de atributos | horses_viewed, viewed_pro_sellers, viewed_sport_elite… | 0.774–0.936 |
| Recurrencia productos | ratio_recurrencia_prods, max_visitas_mismo_producto | 0.805 |

**Decisión:** no se eliminaron. La selección se delegó al feature importance del modelo, que es más robusta para relaciones no lineales. La feature selection post-modelado eliminó las variables redundantes correctas, validando la consistencia con el EDA.

### Outliers de comportamiento (posibles bots)

Usuarios con `horses_viewed` extremadamente alto son casi en su totalidad Lead Bronce. Hipótesis: scraping o comportamiento de bot. Se tratan con capping al P99, no con eliminación, para conservar el patrón de alta actividad sin compra.

### Precios — colas extremas

Ratio max/P99 > 10x en varias columnas de precio. Los outliers corresponden mayoritariamente a Lead Oro — son señal real, no ruido. Se aplica capping al P99 calculado sobre X_train.

---

## 7. Preprocesamiento para el modelado

Todos los pasos se aplican **después del split** para evitar data leakage.

| Paso | Detalle |
|---|---|
| **Split** | 80/20, estratificado por y, random_state=42 |
| **Drop categóricas sin TE** | Se eliminan las categóricas de baja señal (Cramér's V < 0.10) que no entran al Target Encoding |
| **Target Encoding** | `TargetEncoder(smoothing=10)` sobre 9 columnas; fit solo sobre X_train, horse_target como referencia ordinal (Bronce=0, Plata=1, Oro=2) |
| **Capping** | P99 de X_train aplicado a columnas con max/P99 > 2, más columnas fijas por EDA |
| **Split por dominio** | Se filtran las features a `COLS_USER + COLS_HORSE` y `COLS_USER + COLS_PRODS` antes de entrenar cada modelo |

### Las 9 columnas con Target Encoding

```python
COLS_TARGET_ENCODE = [
    # Perfil del usuario
    'user_region', 'user_card_issuer', 'user_domain',
    # Características del caballo más visto (nombres correctos en df_final.parquet)
    'gender_mode', 'breed_family_mode', 'color_mode',
    # Características del producto más visto
    'most_viewed_category', 'most_viewed_brand', 'most_viewed_target_user',
]
```

**Por qué Target Encoding:** convierte cada categoría en la media del target condicionada a esa categoría, preservando la señal en una sola columna. OHE generaría 40+ columnas de baja densidad. El `smoothing=10` evita que categorías con pocas muestras se fijen en la media ruidosa de ese subset.

### Separación de features por dominio

Para evitar contaminación cruzada entre verticales, cada par de modelos recibe únicamente las features relevantes a su dominio:

| Dataset | Features | Total |
|---|---|---|
| `X_train_horse` | 5 usuario + 22 caballos | **27** |
| `X_train_prods` | 5 usuario + 17 productos | **22** |

Las **5 features de usuario** (`user_prestige_score`, `user_antiguedad_dias`, `user_region`, `user_card_issuer`, `user_domain`) son compartidas porque describen el perfil del comprador, no el producto. Las features específicas de cada dominio son mutuamente excluyentes.

---

## 8. Arquitectura del modelo: clasificación en cascada

### El problema con multiclase directo

Con < 1 % de Lead Oro, un clasificador multiclase falla en la clase Oro incluso con class_weight o SMOTE, porque la frontera Plata/Oro es independiente de la frontera Bronce/Plata y ambas se resuelven peor juntas que por separado.

### Dos clasificadores binarios en cascada
```
Usuario
   │
   ▼
[Paso 1] ¿Tiene intención de compra?
    0 = Lead Bronce  →  FIN
    1 = Plata/Oro    →  continúa
              │
              ▼
         [Paso 2] ¿Es comprador de alto valor?
              0 = Lead Plata  →  FIN
              1 = Lead Oro    →  FIN
```

**Ventajas:**
- Cada paso resuelve un problema binario bien definido.
- P2 opera solo sobre el subconjunto no-Bronce, donde Plata/Oro está mucho más balanceado.
- Interpretable: "¿quién tiene intención?" y "¿quién tiene alto valor?" son preguntas separadas.

Esto genera **4 modelos por experimento**: P1-horse, P1-prods, P2-horse, P2-prods.

### Manejo del desbalance por algoritmo

| Modelo | Estrategia | Motivo |
|---|---|---|
| Random Forest | SMOTE antes de entrenar | RF no tiene parámetro nativo de costo por clase tan fino |
| XGBoost P1 | `scale_pos_weight = n_neg / n_pos` | Más eficiente que SMOTE para boosting; evita overfitting en la clase minoritaria |
| XGB P2 en CV | `Pipeline(SMOTE → XGB)` dentro del fold | Evita leakage: SMOTE ve solo el train de cada fold, no el de validación |

### Métrica principal: F2-score Lead Oro

F2 penaliza más los falsos negativos que los falsos positivos. En este contexto, **perder un Lead Oro real es más costoso que contactar a alguien que no era Oro**. F2 es más apropiado que F1 para este objetivo de negocio.

---

## 9. Experimentos y resultados

### Iteración v1 — `LeadScoring.ipynb`

| ID | Modelo | Descripción |
|---|---|---|
| 1 | **RF Baseline** | RandomForest regularizado (max_depth=8, min_samples_leaf=50) + SMOTE |
| 2 | **RF Tuneado** | RF con RandomizedSearchCV (12 iter, sample_frac=0.4) |
| 3 | **XGB Baseline** | XGBoost conservador + scale_pos_weight |
| 4 | **XGB Baseline+TH** | XGB Baseline con threshold tuning sobre P2 (sin reentrenamiento) |
| 5 | **XGB Tuneado** ⭐ | XGB con RandomizedSearchCV (15 iter) + SMOTE-pipeline en P2 |

#### Rendimiento — `horse_target`

| Modelo | F2 macro | F2 Lead Oro | Gap Overfitting P2 |
|---|---|---|---|
| RF Baseline | ~0.42 | ~0.38 | ~0.18 |
| RF Tuneado | ~0.44 | ~0.40 | ~0.14 |
| XGB Baseline | ~0.46 | ~0.44 | ~0.12 |
| XGB Baseline+TH | ~0.46 | ~0.48 | ~0.12 |
| **XGB Tuneado** ⭐ | **~0.48** | **~0.51** | **~0.10** |

#### Rendimiento — `prods_target`

| Modelo | F2 macro | F2 Lead Oro | Gap Overfitting P2 |
|---|---|---|---|
| RF Baseline | ~0.41 | ~0.36 | ~0.19 |
| RF Tuneado | ~0.43 | ~0.38 | ~0.15 |
| XGB Baseline | ~0.45 | ~0.42 | ~0.13 |
| XGB Baseline+TH | ~0.45 | ~0.46 | ~0.13 |
| **XGB Tuneado** ⭐ | **~0.47** | **~0.49** | **~0.11** |

### Iteración v2 — `LeadScoring_v2.ipynb`

Objetivo: explorar LightGBM y CatBoost como alternativas al XGB campeón. Todos los runs se logean con prefijo `v2_*` en el mismo experimento de DagsHub. Se agregan también las features `precio_aspiracional_horse` y `precio_aspiracional_prods`.

| ID | Modelo | Descripción |
|---|---|---|
| v2-1 | **v2_XGB_ThresholdTuning** | XGB reentrenado con nuevo feature set + threshold tuning en v2 |
| v2-2 | **v2_LightGBM_Optuna** | LightGBM con búsqueda bayesiana (Optuna, 30 trials) |
| v2-3 | **v2_CatBoost_Optuna** | CatBoost con categóricas nativas + Optuna (30 trials) |

#### Comparativa v2 vs campeón v1

| Modelo | F2 Oro horse | F2 Oro prods | Gap P2 horse | vs campeón v1 |
|---|---|---|---|---|
| v2_XGB_ThresholdTuning | — | — | — | registrado en DagsHub |
| v2_LightGBM_Optuna | — | — | — | no supera al campeón |
| v2_CatBoost_Optuna | — | — | — | no supera al campeón |

> Los valores exactos están en DagsHub bajo el experimento `EquineLead_LeadScoring`, filtro `tags.version = "v2"`. El campeón vigente sigue siendo **XGB Tuneado (v1)**.

### Observaciones por modelo

**RF Baseline:** establece un piso razonable pero muestra overfitting alto en P2 (gap > 0.18), consistente con la tendencia de RF sin restricciones a memorizar la clase minoritaria.

**RF Tuneado:** el tuning sobre max_depth y min_samples_leaf reduce el gap. La mejora en F2 Oro es modesta — RF tiene limitaciones estructurales para clases tan raras.

**XGB Baseline:** supera a ambos RF gracias a la regularización L1/L2 nativa y a scale_pos_weight.

**XGB Baseline + Threshold Tuning:** experimento exploratorio sobre el XGB Baseline. Bajar el umbral de P2 de 0.5 a ~0.20–0.25 mejora F2 Oro sin reentrenar el modelo. **No es el campeón** — el tuning de hiperparámetros resultó más efectivo como estrategia. El threshold tuning no forma parte del pipeline de inferencia del campeón.

**XGB Tuneado:** la búsqueda sobre {max_depth, learning_rate, subsample, colsample_bytree, reg_alpha, reg_lambda} mejora F2 Oro y reduce el gap de overfitting simultáneamente. Es el campeón actual.

**LightGBM (v2):** entrenamiento más rápido que XGB en CPU gracias a histogram splitting leaf-wise. La búsqueda bayesiana con Optuna exploró un espacio más amplio en el mismo tiempo. No superó al XGB Tuneado en F2 Oro horse a pesar del mayor número de configuraciones evaluadas.

**CatBoost (v2):** el encoding nativo de variables categóricas con ordered target statistics es más robusto que el Target Encoding manual en teoría. En la práctica, el modelo no superó al XGB Tuneado. La ventaja de CatBoost es más pronunciada cuando hay muchas categorías de alta cardinalidad; en este dataset la cardinalidad fue reducida previamente en la FE.

---

## 10. Modelo campeón y feature selection

### Campeón: XGB Tuneado ⭐

Criterio de selección: mayor `f2_lead_oro_horse` entre todos los runs finalizados en MLflow. Se tagea automáticamente como `status=champion` y el anterior campeón pasa a `status=retired`.

El criterio rector es `horse_target` porque los leads que compran caballos representan el mayor valor de negocio en la plataforma.

### Features del modelo campeón

#### 🐴 Modelo Caballos — 27 features

```python
features_caballos = [
    # Usuario (compartidas con modelo productos)
    "user_prestige_score",
    "user_antiguedad_dias",
    "user_region",          # target encoded
    "user_card_issuer",     # target encoded
    "user_domain",          # target encoded
    # Comportamiento en caballos
    "horses_viewed",
    "horses_added_to_cart",
    "max_horse_price_viewed",
    "viewed_premium_horses",
    "viewed_sport_elite",
    "viewed_family_safe",
    "viewed_working_elite",
    "viewed_pro_sellers",
    "has_shipping_viewed",
    "caballos_unicos_vistos",
    "ratio_recurrencia_horse",
    "max_visitas_mismo_caballo",
    "ratio_cart_horse",
    "rango_precio_horse",
    # Categóricas de caballos (target encoded)
    "gender_mode",
    "breed_family_mode",
    "color_mode",
    # Baja señal individual pero del dominio horse
    "avg_horse_age",
    "avg_prestige_score_horses",
    "avg_height",
    "avg_weight",
    "has_registry_viewed",
    "avg_tech_score",
    "avg_temperament",
    "avg_comment_length",
]
```

#### 🛍️ Modelo Productos — 22 features

```python
features_productos = [
    # Usuario (compartidas con modelo caballos)
    "user_prestige_score",
    "user_antiguedad_dias",
    "user_region",          # target encoded
    "user_card_issuer",     # target encoded
    "user_domain",          # target encoded
    # Comportamiento en productos
    "products_viewed",
    "products_added_to_cart",
    "max_product_price_viewed",
    "unique_categories",
    "viewed_waterproof",
    "viewed_leather",
    "viewed_breathable",
    "viewed_uv_protection",
    "viewed_machine_washable",
    "productos_unicos_vistos",
    "ratio_recurrencia_prods",
    "ratio_cart_prods",
    # Categóricas de productos (target encoded)
    "most_viewed_category",
    "most_viewed_brand",
    "most_viewed_target_user",
    # Baja señal individual pero del dominio prods
    "avg_prestige_score_products",
    "avg_product_price_viewed",
]
```

### Feature Selection post-modelado

Se extrae el feature importance del XGB Tuneado y se auditan las variables con `importance < 0.005` en todos los 4 modelos simultáneamente. Las features eliminadas por la auditoría coinciden con las identificadas como ruido/redundantes en el EDA, validando la consistencia del análisis exploratorio.

### Comparación full vs. seleccionado

| Target | Métrica | Full | Sel. | Delta |
|---|---|---|---|---|
| horse | F2 Lead Oro | ~0.51 | ~0.51 | ≈ 0.00 |
| horse | Gap Overfitting P2 | ~0.10 | ~0.08 | **−0.02** |
| prods | F2 Lead Oro | ~0.49 | ~0.49 | ≈ 0.00 |
| prods | Gap Overfitting P2 | ~0.11 | ~0.09 | **−0.02** |

La feature selection mantiene el rendimiento y reduce el overfitting — el modelo seleccionado generaliza mejor a datos nuevos.

---
## 11. Tracking de experimentos con MLflow / DagsHub

Cada run logea automáticamente:

- **Parámetros:** hiperparámetros de P1 y P2 (prefijo `p1_` / `p2_`), tipo de modelo, estrategia de balanceo, umbrales de threshold tuning.
- **Métricas:** `f2_macro`, `f2_lead_oro`, `f2_lead_plata`, `f2_paso1`, `f2_paso2_test`, `f2_paso2_train`, `overfit_gap_p2` — por cada target.
- **Artefactos:** 4 modelos `.pkl`, feature importance (top 15), matrices de confusión normalizadas, curvas Precision-Recall con AUC-PR.
- **Tags:** `model_type`, `pipeline`, `version` (v1 / v2), `status` (champion / retired).

```
https://dagshub.com/aletbm/S02-26-E45-Data_Science_EquineLead.mlflow
Experimento: EquineLead_LeadScoring
Runs v1: sin prefijo
Runs v2: prefijo v2_*  |  filtro: tags.version = "v2"
```

---

## 12. Estructura del pipeline de producción

```
features.py  →  train.py  →  model.py
     │               │            │
 df_final.parquet  MLflow     predicciones
                  (DagsHub)
```

| Script | Responsabilidad |
|---|---|
| `features.py` | Carga las 5 tablas, limpieza, FE, merges, targets, agrega por usuario, guarda `df_final.parquet` |
| `metrics.py` | Funciones de evaluación y logging (importado por `train.py`) |
| `train.py` | Carga `df_final.parquet`, preprocesa (TE + capping + split por dominio), entrena todos los modelos, loga en MLflow, selecciona campeón, serializa artefactos |
| `model.py` | Carga el run campeón desde MLflow, carga artefactos de preprocesamiento, expone `predict(X)` |

### Artefactos serializados por `train.py`

| Archivo | Contenido | Nota |
|---|---|---|
| `modelo_p1_horse.pkl` | XGBoost P1 caballos | |
| `modelo_p1_prods.pkl` | XGBoost P1 productos | |
| `modelo_p2_horse.pkl` | XGBoost P2 caballos | |
| `modelo_p2_prods.pkl` | XGBoost P2 productos | |
| `target_encoder.pkl` | TargetEncoder fit sobre X_train | 9 columnas, smoothing=10 |
| `limites_capping.pkl` | Dict col → límite P99 | Calculado sobre X_train |
| `cols_horse.pkl` | Lista de features del dominio caballos | **Nuevo** — reemplaza `cols_v2.pkl` |
| `cols_prods.pkl` | Lista de features del dominio productos | **Nuevo** — reemplaza `cols_v2.pkl` |
| `cols_user.pkl` | Lista de 5 features de usuario compartidas | **Nuevo** |

---

## 13. Decisiones descartadas y su justificación

| Decisión descartada | Motivo |
|---|---|
| Clasificador multiclase directo | Con < 1 % de Lead Oro el modelo aprende a ignorar la clase; F2 Oro resulta cercano a 0 incluso con SMOTE |
| Eliminar features colineales antes del modelado | La correlación lineal no captura señal no lineal; se delegó al feature importance |
| One-Hot Encoding para categóricas | Genera 40+ columnas de baja densidad; Target Encoding es más compacto y captura la relación con el target directamente |
| Eliminar outliers de precio | Los outliers son mayoritariamente Lead Oro — son señal, no ruido; se aplica capping en su lugar |
| Incluir columna `city` | 800+ categorías, ninguna con > 0.5 % de frecuencia, Cramér's V < 0.02 con ambos targets |
| SMOTE para XGBoost fuera del pipeline de CV | SMOTE antes del CV contamina los folds de validación (leakage); se usa `Pipeline(SMOTE→XGB)` |
| GridSearchCV completo para XGB | Espacio de hiperparámetros demasiado grande para búsqueda exhaustiva; RandomizedSearchCV con 15 iteraciones es suficiente |
| F1-score como métrica principal | F1 penaliza igual FP y FN; perder un Lead Oro (FN) es más costoso que un falso positivo — F2 es más apropiado |
| LightGBM como modelo final | No superó al XGB Tuneado en F2 Lead Oro horse pese a mayor velocidad de entrenamiento y búsqueda bayesiana con Optuna |
| CatBoost con categóricas nativas | El encoding nativo no mejoró respecto al Target Encoding del pipeline XGB; la reducción de cardinalidad previa en FE ya limita la ventaja de CatBoost |
| `precio_aspiracional_horse/prods` como features activas | Ratio max/avg redundante con `max_horse_price_viewed` que ya captura la misma señal con mayor poder discriminativo |
| `cols_v2.pkl` genérico para ambos dominios | Reemplazado por `cols_horse.pkl` y `cols_prods.pkl` separados para que `model.py` filtre correctamente sin lógica condicional adicional |
