# 📊 Registro de Experimentos con MLflow en DagsHub

Este tutorial explica **cómo levantar el entorno con `uv` y cómo registrar experimentos en MLflow usando los templates del proyecto**. Está pensado para Data Scientists del equipo EquineLead.

> ⚠️ **Requisito obligatorio**: para poder registrar experimentos en MLflow **debés ser colaborador del repositorio en DagsHub**. Si no lo sos, vas a ver errores de permisos (401/403).

---

## 1️⃣ Levantar el entorno de trabajo (uv)

⚠️ **Importante**: el entorno **NO se construye de cero**. Este repositorio ya incluye:

* `pyproject.toml`
* `uv.lock`

Estos archivos garantizan un entorno **reproducible y estandarizado para todo el equipo**.

### Paso 1 – Instalar uv (si no lo tenés)

```bash
pip install uv
```

### Paso 2 – Crear el entorno virtual y sincronizar dependencias a partir del lockfile (reproducible)

```bash
uv sync --locked
```

📌 Este comando instala **exactamente** las versiones fijadas en `uv.lock`.

---

## 2️⃣ Dónde viven los experimentos

Los experimentos de ML están organizados en:

```text
src/experiments/
├── engine/
├── leads_horses/
└── leads_products/
```

Cada carpeta representa **un experimento de negocio distinto**.

Dentro de cada experimento hay siempre los mismos templates:

```text
features.py   # Feature engineering
model.py      # Entrenamiento del modelo
metrics.py    # Métricas
train.py      # Orquestador + MLflow
```

⚠️ **Regla del equipo**: los DS solo modifican estos archivos. No tocar `misc/`, `flows/` ni infra.

---

## 3️⃣ Qué tenés que modificar como Data Scientist

### 🧠 `train.py` – Configuración personal (OBLIGATORIO)

En la parte superior del archivo:

```python
# ==================================
# DATA SCIENTIST PERSONAL CONFIG
# ==================================
RUN_NAME = "baseline_xgboost_v1_YYYYMMDD_HHMMSS"
DS_NAME = "Tu_Nombre_Apellido"
STAGE = "training"
```

🔧 **Debés cambiar**:

* `RUN_NAME`: nombre descriptivo del experimento
* `DS_NAME`: tu nombre (queda auditado en MLflow)
* `STAGE`: normalmente `training` (no cambiar salvo indicación del MLE)

---

### 📦 Dataset

```python
PATH_DATA = Path("./data/clean")
DATASET_NAME = "dataset_name.parquet"
```

🔧 Cambiar solo si usás otro dataset **aprobado**.

---

## 4️⃣ Feature Engineering – `features.py`

En este archivo se define **qué datos entran al modelo y cómo se construyen**.

### Qué se debe modificar

Buscá la función principal (por ejemplo `build_features`) y **modificá solo estas secciones**:

1. **Selección de columnas (features y target)**

   ```python
   features = [
       "col_1",
       "col_2",
       "col_3",
   ]

   target = "target_column"
   ```

2. **Transformaciones**

   ```python
   df_features = df[features]
   # acá podés:
   # - crear features nuevas
   # - normalizar / escalar
   # - encodear variables categóricas
   ```

3. **Split de datos**

   ```python
   X_train, X_val, y_train, y_val = train_test_split(
       df_features,
       df[target],
       test_size=0.2,
       random_state=random_state,
   )
   ```

🚫 **No modificar**:

* Imports compartidos
* Firma de la función
* El return (`X_train, X_val, y_train, y_val`)

📌 El objetivo es que `train.py` no cambie nunca.

---

## 5️⃣ Entrenamiento – `model.py`

Ejemplo actual:

```python
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    random_state=random_state,
    n_jobs=-1
)
```

🔧 **Modificar cuando**:

* Cambiás el algoritmo
* Ajustás hiperparámetros

📌 **Regla clave**:

* Scikit-learn / wrappers → `mlflow.sklearn.log_model`
* DL / frameworks nativos → logger específico

---

## 6️⃣ Métricas – `metrics.py`

Ejemplo:

```python
return {
    "rmse": root_mean_squared_error(y_val, preds),
    "mae": mean_absolute_error(y_val, preds),
}
```

🔧 **Acá es donde tenés que modificar si usás**:

* Otras métricas
* Clasificación (accuracy, f1, auc, etc.)
* Métricas custom

📌 Todo lo que devuelva este diccionario se registra automáticamente en MLflow:

```python
for k, v in metrics.items():
    mlflow.log_metric(k, v)
```

---

## 7️⃣ Registro de Dataset (OBLIGATORIO)

En `train.py`:

```python
log_dataset_metadata(
    name="horses_listings",
    version="v1.0.1",
    path="/clean/horses_listings_limpio.parquet",
    n_rows=df.shape[0],
    n_cols=df.shape[1],
)
```

🔧 **Debés cambiar**:

* `name`
* `version`
* `path`

📌 Esto es clave para trazabilidad y auditoría.

---

## 8️⃣ Reproducibilidad y entorno (NO TOCAR)

```python
mlflow.log_param("random_state", SEED)
mlflow.log_param("python_version", sys.version)
mlflow.log_param("os", platform.system())
```

Esto garantiza que el experimento sea reproducible.

---

## 9️⃣ Información del modelo (OBLIGATORIO)

En `train.py`:

```python
# =====================
# Model Info
# =====================
mlflow.log_param("model_type", model.__class__.__name__)
mlflow.log_param("model_family", "tree-based")
```

### Qué debés modificar

* `model_type`: **se completa automáticamente**, no tocar.
* `model_family`: **DEBÉS ajustarlo según el modelo usado**.

Ejemplos válidos:

| Tipo de modelo               | model_family    |
| ---------------------------- | --------------- |
| RandomForest, XGBoost        | `tree-based`    |
| Linear / Logistic Regression | `linear`        |
| Neural Networks              | `deep-learning` |
| Reglas / heurísticas         | `rule-based`    |
| Modelos custom               | `custom`        |

📌 Esto se usa luego para:

* Filtrar experimentos
* Automatizar despliegues
* Análisis comparativos

---

## 🔟 Registrar el modelo

Ejemplo actual:

```python
mlflow.sklearn.log_model(
    model,
    artifact_path="model_engine"
)
```

📌 **Usar el logger correcto según el framework**:

* sklearn / XGBoost wrapper → `mlflow.sklearn.log_model`
* PyTorch → `mlflow.pytorch.log_model`
* TensorFlow → `mlflow.tensorflow.log_model`
* Custom → `mlflow.pyfunc.log_model`

🚫 No mezclar loggers.

---

## 🔟 Ejecutar el experimento

Desde la raíz del repo:

```bash
python src/experiments/engine/train.py
```

Si todo está bien:

* El run aparece en MLflow (DagsHub)
* Quedan registrados:

  * Métricas
  * Parámetros
  * Dataset
  * Modelo

---

## 🚨 Errores comunes

### ❌ No puedo registrar experimentos

✔ Verificá que seas **colaborador del repo en DagsHub**

### ❌ Error de credenciales

✔ Revisá `.env` y configuración de MLflow

---

## ⭐ Best Practices del equipo (OBLIGATORIAS)

* Usar nombres de runs descriptivos y comparables
* Un cambio conceptual = un run nuevo
* No sobreescribir métricas existentes
* Loguear **SIEMPRE** dataset + versión
* Mantener consistencia en `model_family`
* Todo experimento debe ser reproducible con `uv sync --locked`

---

## ✅ Checklist final para DS (OBLIGATORIO)

Antes de dar por válido un experimento, **TODOS** los puntos deben cumplirse:

### 🧪 Entorno

* [ ] El repo fue actualizado (`git pull`)
* [ ] El entorno se creó con `uv sync --locked`
* [ ] No se instalaron paquetes manualmente con `pip install`, sino con `uv add`

### 🧠 Configuración del experimento (`train.py`)

* [ ] `RUN_NAME` es descriptivo y único (incluye idea + fecha)
* [ ] `DS_NAME` corresponde al autor real del experimento
* [ ] `STAGE` es correcto (`training` salvo indicación del MLE)

### 📦 Dataset

* [ ] El dataset usado está en `data/clean/`
* [ ] El nombre del archivo es correcto
* [ ] El dataset fue logueado con `log_dataset_metadata`
* [ ] La versión del dataset fue incrementada si hubo cambios

### 🧠 Feature Engineering (`features.py`)

* [ ] No se cambió la firma ni el return de la función
* [ ] El split es reproducible (usa `random_state`)

### 📊 Métricas (`metrics.py`)

* [ ] Los nombres de métricas son claros y estables
* [ ] Todas las métricas retornadas se registran en MLflow

### 🤖 Modelo (`model.py` + `train.py`)

* [ ] El algoritmo está claramente definido
* [ ] Los hiperparámetros son explícitos
* [ ] `model_family` refleja correctamente el tipo de modelo
* [ ] Se usa el logger de MLflow correcto para el framework

### 🔁 Reproducibilidad

* [ ] `random_state` está logueado
* [ ] Versión de Python y OS están logueadas
* [ ] El experimento puede re-ejecutarse sin cambios manuales

### 🔐 DagsHub / MLflow

* [ ] Sos colaborador del repositorio en DagsHub
* [ ] El run aparece correctamente en la UI de MLflow
* [ ] Se registraron parámetros, métricas, artifacts y modelo

---

📌 **Si algún punto falla, el experimento NO se considera válido.**
