import os
from pathlib import Path

from dotenv import load_dotenv

# Carga el .env desde la raíz del proyecto
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# ── Modelos y artefactos ──────────────────────────────────────────────────────
MODELS_DIR = "src/models/champion"  # donde están los 4 .pkl de modelos
ARTIFACTS_DIR = "src/models/champion"  # donde están los 5 .pkl de preprocesamiento

# ── Datos ─────────────────────────────────────────────────────────────────────
# Dataset de referencia (mismo formato que df_final.parquet de entrenamiento)
REFERENCE_DATA_PATH = "data/clean/df_final.parquet"

# Dataset de producción — mismo formato crudo que entrenamiento.
# Reemplazá este archivo con tus logs reales de producción.
CURRENT_DATA_PATH = "data/production/data_drift.parquet"

# ── Columnas de monitoreo ─────────────────────────────────────────────────────
TARGET_COL = "horse_target"  # ground truth  ('Lead Bronce' | 'Lead Plata' | 'Lead Oro')
PREDICTION_COL = "prediction"  # predicción del modelo

# ── Reportes ──────────────────────────────────────────────────────────────────
REPORT_DIR = "src/monitoring/reports/"

# ── Drift ─────────────────────────────────────────────────────────────────────
DRIFT_THRESHOLD = 0.3  # proporción de features drifteadas que dispara alerta

# ── Slack ─────────────────────────────────────────────────────────────────────
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
