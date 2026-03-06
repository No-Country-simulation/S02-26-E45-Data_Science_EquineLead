import os

# ── MLflow ────────────────────────────────────────────────────────────────────
MODEL_NAME = "model_engine"
MODEL_ALIAS = "production"  # stage usado en DagsHub

# ── Datos ─────────────────────────────────────────────────────────────────────
# Dataset de referencia (entrenamiento)
REFERENCE_DATA_PATH = "data/clean/horses_listings_limpio.parquet"

# Dataset de producción — reemplazá esta ruta con tus datos reales.
# Puede ser un CSV/parquet generado por logs de Gradio, una query a BD, etc.
CURRENT_DATA_PATH = "data/monitoring/current_data.parquet"

# ── Features esperadas por el modelo ─────────────────────────────────────────
FEATURE_COLS = ["breed", "color", "price"]
TARGET_COL = "label"  # columna de ground truth (real o simulada)
PREDICTION_COL = "prediction"  # columna de predicción del modelo

# ── Reportes ──────────────────────────────────────────────────────────────────
REPORT_DIR = "monitoring/reports/"

# ── Drift ─────────────────────────────────────────────────────────────────────
DRIFT_THRESHOLD = 0.3  # proporción de features drifteadas que dispara alerta

# ── Slack ─────────────────────────────────────────────────────────────────────
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
