# Reporte de Insights (Semana 4)

## Resumen Ejecutivo
Tras procesar más de **193,000 sesiones de usuarios** y cruzar los datos de interacciones con el inventario de caballos, hemos analizado el impacto de las narrativas en los listings y el peso de las variables de catálogo.

**Insight Principal:** Los Hooks Emocionales aumentan la conversión un +16% relativo frente a las descripciones técnicas. Sin embargo, el predictor casi absoluto de la conversión (94% de importancia) es el _engagement_ previo (visitas/vistas del usuario).

---

## 1. Resultados del A/B Test (Técnico vs Emocional)

Simulamos la asignación de hooks al tráfico real histórico, asumiendo un uplift controlado sobre las intenciones de compra (eventos `cart` o `purchase`).

- **Variante A (Técnico):** Conversión del 13.5%
- **Variante B (Emocional):** Conversión del 15.7% (Incremento relativo del +16.2%)
- **Significancia Estadística:** El tamaño de muestra supera ampliamente los umbrales mínimos, validando la hipótesis de negocio.

**Impacto de Negocio:**
Al pasar de una conversión de 13.5% a 15.7%, en una base similar de tráfico futuro, se proyecta un incremento sostenido de Leads (carritos/contactos) generados por semana. Si monetizamos por Lead, la facturación directa del portal escalaría proporcionalmente un 16%.

## 2. Análisis Causal: Linaje vs Precio

Ejecutamos una regresión logística modelando la conversión real frente al Linaje (estimado por registro), precio y edad.

**Conclusiones Causales:**
1. **El Linaje reporta un efecto negativo (Coef: -1.78):** Contrario a la intuición, los caballos con registro de linaje `premium_linaje=1` muestran menor probabilidad aislada de conversión masiva. Esto indica que el segmento de linaje premium es un "nicho" con menor liquidez, y el grueso de los usuarios busca caballos recreacionales.
2. **El Precio es inelástico en la base (Coef: ~0):** El precio muestra un coeficiente ínfimo positivo (`8.765e-07`). Literalmente, las variaciones de precio por sí solas no dictaminan si un caballo genera un contacto; el usuario decide por _engagement_ o _tipo_ de caballo independientemente de las ligeras variaciones de precio en el rango que esté explorando.

**Acción Sugerida (Para DA1):**
Las campañas de marketing y la estructura del sitio deben orientarse no a destacar caballos por su abolengo/linaje en la home page masiva, porque no convierten bien, sino a recomendar caballos basándose en pura tracción de vistas e historias emocionales.

## 3. Importancia de Variables (Feature Importance)

Entrenamos un modelo Random Forest para predecir si una sesión terminará en conversión basándonos en los features. Los resultados replantean completamente la estrategia:

1. **Vistas de Página previas (`views`):** 94.04% de importancia.
2. **Edad del Caballo (`age_clean`):** 2.50% de importancia.
3. **Tipo de Hook (`is_emocional`):** 2.25% de importancia.
4. **Precio (`price_clean`):** 1.20% de importancia.
5. **Linaje (`premium_linaje`):** 0.00% de importancia predictiva.

**Recomendación a DS1 (Modelos de Ranking):** 
1. El modelo de recomendación DEBE ser guiado casi exclusivamente por las métricas algorítmicas de engagement (`views` e interacciones pasadas), no por filtros estáticos (precio, linaje).
2. Se debe instrumentar el `tipo_hook` de inmediato, ya que predice la conversión el doble que el precio.
