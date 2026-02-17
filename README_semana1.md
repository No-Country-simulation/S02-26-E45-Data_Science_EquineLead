# 🐴 Proyecto EquineLead - Semana 1: Segmentación de Leads

Este proyecto forma parte de la simulación de **No Country**. En esta primera etapa, nos enfocamos en procesar datos crudos de una plataforma ecuestre para identificar el valor potencial de los usuarios.

## 🎯 Objetivo
Transformar datos de comportamiento (sesiones) y perfiles de usuario en una clasificación accionable para el equipo de marketing.

## 🛠️ Tecnologías Utilizadas
- **Python / Pandas**: Para el procesamiento de datos.
- **Pyarrow**: Para la gestión de archivos .parquet.
- **Git Bash / UV**: Para el control del entorno y versiones.

## 📊 Proceso de Ingeniería de Datos
1. **Normalización:** Se "aplanaron" diccionarios complejos en la columna `job_info`, extrayendo cargos y empresas.
2. **Unificación:** Se consolidaron múltiples catálogos de caballos (`EquineNow` y `HorseDeals`) resolviendo conflictos de nombres de columnas (Case-sensitive).
3. **Métricas de Comportamiento:** Se calcularon visualizaciones por usuario en las categorías de caballos y productos.

## 💎 Resultados de la Segmentación
Aplicando reglas de negocio, clasificamos la base de datos de la siguiente manera:

| Lead Tier | Cantidad | Descripción |
| :--- | :--- | :--- |
| **Oro** 🏆 | 210 | Compradores de caballos de alto valor (>$50,000) |
| **Plata** 🥈 | 17,498 | Usuarios con compras de productos o caballos base |
| **Bronce** 🥉 | ~ | Usuarios con intención (abandonaron carrito) |
| **Interesado** | 182,292 | Usuarios en etapa de exploración |

---
*Próximo paso: Desarrollo del motor de recomendación (Semana 2).*



---

# 🐴 EquineLead Project - Week 1: Lead Segmentation

This project is part of the **No Country** simulation. In this first stage, we focused on processing raw data from an equine platform to identify potential user value.

## 🎯 Objective
Transform behavioral data (sessions) and user profiles into an actionable classification for the marketing team.

## 🛠️ Technologies Used
- **Python / Pandas**: Data processing.
- **Pyarrow**: .parquet file management.
- **Git Bash / UV**: Environment and version control.

## 📊 Data Engineering Process
1. **Normalization:** "Flattened" complex dictionaries in the `job_info` column, extracting job titles and companies.
2. **Unification:** Consolidated multiple horse catalogs (`EquineNow` and `HorseDeals`) by resolving case-sensitive column name conflicts.
3. **Behavioral Metrics:** Calculated user view counts for both horse and product categories.

## 💎 Segmentation Results
Applying business rules, we classified the database as follows:

| Lead Tier | Count | Description |
| :--- | :--- | :--- |
| **Gold** 🏆 | 210 | High-value horse buyers (>$50,000) |
| **Silver** 🥈 | 17,498 | Users with product or base horse purchases |
| **Bronze** 🥉 | ~ | High-intent users (abandoned cart) |
| **Interested** | 182,292 | Exploration-stage users |