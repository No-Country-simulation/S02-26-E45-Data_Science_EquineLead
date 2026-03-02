# 🐴 Proyecto EquineLead - README

## 🇪🇸 Versión en Español

### 📋 Resumen del Proyecto
Este proyecto forma parte de la simulación de **No Country**. Nos enfocamos en procesar datos crudos de una plataforma ecuestre para identificar el valor potencial de los usuarios y preparar el terreno para un motor de recomendación inteligente.

### 🎯 Objetivo
Transformar datos de comportamiento (sesiones) y perfiles de usuario en una clasificación accionable (**Lead Scoring**) para optimizar las estrategias de marketing y ventas.

### 🛠️ Tecnologías Utilizadas
* **Python / Pandas:** Procesamiento y limpieza de datos.
* **Pyarrow:** Gestión eficiente de archivos `.parquet`.
* **Matplotlib / Seaborn:** Visualización de datos y análisis exploratorio (EDA).
* **Git Bash / UV:** Control de versiones y gestión de entornos virtuales.

### 📊 Proceso de Ingeniería de Datos (Hitos)
1. **Normalización:** Se "aplanaron" estructuras complejas en la columna `job_info`, extrayendo cargos y empresas para perfilar mejor al usuario.
2. **Unificación Multicanal:** Se consolidaron **5 bases de datos** críticas: Usuarios, Caballos, Productos, Sesiones de Equinos y Sesiones de Accesorios.
3. **Resolución de Conflictos:** Se estandarizaron nombres de columnas (`item_id` vs `horse_id`) y se corrigieron discrepancias de mayúsculas/minúsculas (*Case-sensitivity*).
4. **Limpieza de Datos:** Procesamiento masivo de **200,000 registros**, gestionando valores nulos y asegurando la integridad de los tipos de datos numéricos.

### 💎 Resultados de la Segmentación Final
Tras el cruce de sesiones y catálogos, la base de datos se clasifica de la siguiente manera:

| Categoría de Lead | Cantidad | Descripción |
| :--- | :--- | :--- |
| **Oro 🏆** | **5,913** | Usuarios con interés activo en caballos de alto valor (>$50,000). |
| **Plata 🥈** | **187,453** | Usuarios interesados en mercado medio y accesorios premium. |
| **Bronce 🥉** | **6,634** | Usuarios nuevos o con baja actividad reciente registrado. |

---

## 🇺🇸 English Version

### 📋 Project Overview
This project is part of the **No Country** simulation. We focus on processing raw data from an equine platform to identify potential user value and lay the groundwork for an intelligent recommendation engine.

### 🎯 Objective
Transform behavioral data (sessions) and user profiles into actionable classification (**Lead Scoring**) to optimize marketing and sales strategies.

### 🛠️ Technologies Used
* **Python / Pandas:** Data processing and cleaning.
* **Pyarrow:** Efficient `.parquet` file management.
* **Matplotlib / Seaborn:** Data visualization and Exploratory Data Analysis (EDA).
* **Git Bash / UV:** Version control and virtual environment management.

### 📊 Data Engineering Process (Milestones)
1. **Normalization:** "Flattened" complex structures in the `job_info` column, extracting job titles and companies for better user profiling.
2. **Multi-channel Unification:** Consolidated **5 critical databases**: Users, Horses, Products, Equine Sessions, and Accessory Sessions.
3. **Conflict Resolution:** Standardized column names (`item_id` vs `horse_id`) and fixed case-sensitivity discrepancies.
4. **Data Cleaning:** Processed **200,000 records**, handling null values and converting data types to ensure accurate calculations.

### 💎 Final Segmentation Results
After a massive cross-reference of sessions and catalogs, the database is classified as follows:

| Lead Tier | Count | Description |
| :--- | :--- | :--- |
| **Gold 🏆** | **5,913** | Users with active interest in high-value horses (>$50,000). |
| **Silver 🥈** | **187,453** | Active users interested in the mid-market and premium accessories. |
| **Bronze 🥉** | **6,634** | New users or those with low recent activity on the platform. |