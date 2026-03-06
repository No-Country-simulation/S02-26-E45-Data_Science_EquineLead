# 🐴 Motor de Recomendación: EquineLead (Full Stack Data Science)

Este repositorio contiene el desarrollo integral de la inteligencia de datos de **EquineLead**, desde el procesamiento masivo de leads hasta la implementación de un motor de búsqueda vectorial de alta fidelidad.

## 📋 Resumen del Proyecto
Transformamos datos crudos de una plataforma ecuestre en un sistema de recomendación inteligente. El proyecto evolucionó de una segmentación básica de usuarios (Lead Scoring) a un motor de búsqueda basado en **K-Nearest Neighbors (KNN)** con métricas de **Similitud de Coseno**.

---

## 🛠️ Stack Tecnológico
* **Lenguajes:** Python (Pandas, NumPy, SciPy).
* **Machine Learning:** Scikit-Learn (NearestNeighbors, TfidfVectorizer, MinMaxScaler).
* **Infraestructura:** UV (Package Manager), Pyarrow (.parquet).
* **MLOps:** MLflow & DagsHub (Tracking de experimentos).

---

## 📊 Hito 1: Ingeniería de Datos y Lead Scoring
Procesamos más de **200,000 registros** para clasificar el valor potencial de los usuarios y preparar el terreno para el motor de recomendación.

### Logros Clave:
* **Normalización:** Aplanamiento de estructuras complejas en la columna `job_info`.
* **Unificación Multicanal:** Consolidación de 5 bases de datos (Usuarios, Caballos, Productos y Sesiones).
* **Resultados de Segmentación (Lead Tier):**
    * 🏆 **Oro:** 5,913 leads de alto valor (interés >$50,000).
    * 🥈 **Plata:** 187,453 leads interesados en mercado medio y accesorios premium.
    * 🥉 **Bronce:** 6,634 leads nuevos o con baja actividad reciente.

---

## 🧠 Hito 2: Motor de Recomendación (IA)
Evolucionamos de un filtrado básico basado en reglas a un sistema de **Búsqueda Vectorial** de alta fidelidad.

### Características Técnicas:
* **NLP & Feature Engineering:** Uso de `TF-IDF Vectorizer` para procesar la semántica de razas y pelajes.
* **Optimización de Memoria:** Implementación de matrices **CSR (Compressed Sparse Row)** para el manejo eficiente de datos dispersos.
* **Algoritmo:** **K-Nearest Neighbors (KNN)** con métrica de **Similitud de Coseno**, logrando una precisión promedio del **74.65%**.

### 📥 Especificaciones para la API (Features)
Para la integración con el Backend, el modelo consume las siguientes variables:

| Variable | Tipo | Descripción |
| :--- | :--- | :--- |
| **`price`** | Float | Precio del caballo (Gama económica). |
| **`height_hh`** | Float | Altura física del ejemplar. |
| **`age`** | Int | Edad en años. |
| **`breed`** | Vectorized | Raza procesada semánticamente. |
| **`color`** | Vectorized | Color/Pelaje procesado semánticamente. |



---

## 🚀 Hito 3: MLOps e Integración Final (Cuaderno 4)
En la fase final, el modelo fue profesionalizado para asegurar su despliegue y monitoreo continuo:

* **Tracking con MLflow:** Registro de parámetros de entrenamiento, versiones de Python y métricas de rendimiento en tiempo real.
* **DagsHub Integration:** Sincronización de artefactos de modelo y datasets en la nube para colaboración fluida con el equipo de Backend.
* **Métrica de Calidad:** Monitoreo de la **Distancia Media de Coseno** para garantizar que el sistema identifica consistentemente perfiles compatibles.

---

## 📂 Guía de Uso
Para ejecutar el motor de recomendación y registrar el experimento en DagsHub:

```bash
uv run python src/experiments/engine/train.py
