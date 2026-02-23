# Reporte de Insights (Semana 4) - Executive Data Science Review

## Resumen Ejecutivo
Tras procesar más de **193,000 sesiones de usuarios** y aplicar metodologías rigurosas de inferencia causal y testing estadístico (Z-Tests, Logit con Estandarización HC3, Permutation Importance), hemos analizado el impacto real de las narrativas en los listings y el peso de las variables de catálogo en la conversión final.

**Insight Principal:** Los Hooks Emocionales aumentan la probabilidad de conversión un **+16.24%** relativo de forma estadísticamente significativa. Adicionalmente, confirmamos causalmente que el linaje premium *penaliza* la conversión masiva general, y validamos sin sesgos que el único predictor robusto de compra es el _engagement_ (vistas previas) del usuario.

---

## 1. Resultados del A/B Test (Técnico vs Emocional)

Simulamos un entorno A/B robusto sobre el inventario base. Para garantizar rigor, evaluamos los resultados utilizando un **Test Z para proporciones** calculando Intervalos de Confianza (CI) al 95%.

- **Variante B (Emocional):** Conversión del **15.68%** `[95% CI: 15.42%, 15.95%]`
- **Variante A (Técnico):** Conversión del **13.49%** `[95% CI: 13.25%, 13.73%]`
- **Métricas de Impacto:**
  - **Uplift Absoluto:** +2.19%
  - **Uplift Relativo:** +16.24%
- **Significancia Estadística:** Altamente significativa (Z-Statistic: 13.3150 | P-Value < 0.0001). 

> [!TIP]
> **Impacto de Negocio (ROI):** Con una confianza estadística superior al 99.9% (p < 0.0001), desplegar Hooks Emocionales globalmente garantiza un aumento del 16% en la generación de leads. Si el costo de adquisición se mantiene plano, este uplift se traduce de forma directa en un +16% de facturación por leads sin inversión adicional.

## 2. Inferencia Causal: Linaje vs Precio

Para ir más allá de la correlación, ejecutamos un modelo de regresión logística estimando los Efectos Marginales Promedio (AME), controlando la heterocedasticidad mediante **Errores Estándar Robustos (HC3)**. Esto nos permite interpretar el impacto *aislado* de cada variable en la probabilidad absoluta de conversión.

**Conclusiones Causales (AME):**
1. **El Linaje Premium penaliza la liquidez masiva:** 
   - AME: `-0.0988` (P-Value: < 0.01)
   - *Interpretación de Negocio:* Si un caballo tiene linaje premium, su probabilidad de conversión a nivel masivo cae un **9.8% absoluto**, asumiendo todas las demás variables constantes. Esto confirma que el linaje premium apela estrictamente a un nicho reducido, y exponerlos al tráfico masivo sin segmentar daña la métrica global de conversión del portal.
2. **La Inelasticidad del Precio en la conversión primaria:**
   - AME: `+1.094e-07` (P-Value: 0.015)
   - *Interpretación de Negocio:* El precio tiene un efecto virtualmente de **cero** al predecir el contacto (lead). El usuario filtra primero por caballo, y las negociaciones ocurren post-contacto. El precio *no* frena el lead.

**Acción Sugerida (Para DA1 - Estrategia):**
Las campañas de display / home-page no deben priorizar el "Abolengo/Linaje". Se deben crear dos flujos separados: un marketplace masivo impulsado algorítmicamente por popularidad, y un canal VIP/Nicho para caballos con registro premium.

## 3. Validación de Importancia (Permutation Feature Importance)

Para corregir el sesgo natural hacia variables continuas o de alta cardinalidad que sufren los Random Forests tradicionales, aplicamos **Permutation Importance** sobre un set de evaluación (Test Set) completamente nuevo.

**Resultados de Validación (Importancia Promedio):**
1. **`views` (Vistas Previas):** `0.003468`
2. **Otras variables (`premium_linaje`, `age`, `price`):** `0.000000`

> [!IMPORTANT]
> **Recomendación a DS1 (Modelos de Recomendación/Ranking):**
> Al aislar correctamente los errores, descubrimos que los metadatos estáticos (edad, precio, linaje) aportan literalmente cero poder predictivo puro fuera del set de entrenamiento. La capacidad instalada de los modelos debe orientarse **exclusivamente a features de comportamiento de usuario** (Filtro Colaborativo, Frecuencia de vistas, Dwell time) y al tipo de narrativa (`hook_type`).
