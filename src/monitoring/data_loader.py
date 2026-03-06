from pathlib import Path

import config as cfg
import numpy as np
import pandas as pd


def load_reference_data() -> pd.DataFrame:
    """Carga el dataset de entrenamiento como referencia."""
    df = pd.read_parquet(cfg.REFERENCE_DATA_PATH)
    df.columns = [c.lower().strip() for c in df.columns]
    df = df[cfg.FEATURE_COLS].copy()

    # Simular ground truth para referencia (en producción reemplazar con labels reales)
    df[cfg.TARGET_COL] = _simulate_labels(len(df))
    df[cfg.PREDICTION_COL] = _simulate_labels(len(df))

    return df


def load_current_data() -> pd.DataFrame:
    """
    Carga los datos de producción actuales.

    Reemplazá esta función con tu fuente real de datos:
        - CSV/parquet de logs de Gradio
        - Query a base de datos
        - Archivo generado por el logger de la API
    """
    path = Path(cfg.CURRENT_DATA_PATH)

    if not path.exists():
        print(f"⚠️  Current data not found at {path}. Generating synthetic data...")
        return _generate_synthetic_data()

    ext = path.suffix
    if ext == ".parquet":
        df = pd.read_parquet(path)
    elif ext == ".csv":
        df = pd.read_csv(path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    df.columns = [c.lower().strip() for c in df.columns]
    return df[cfg.FEATURE_COLS + [cfg.TARGET_COL, cfg.PREDICTION_COL]]


def _simulate_labels(n: int) -> list:
    """Simula ground truth binario (0=no compra, 1=compra)."""
    return np.random.choice([0, 1], size=n, p=[0.7, 0.3]).tolist()


def _generate_synthetic_data(n: int = 500) -> pd.DataFrame:
    """
    Genera datos sintéticos de producción con distribución levemente desviada
    respecto al dataset de entrenamiento para simular drift.

    Reemplazá con datos reales cuando estén disponibles.
    """
    breeds = ["andalusian", "thoroughbred", "quarter horse", "arabian", "warmblood"]
    colors = ["bay", "black", "chestnut", "grey", "palomino"]

    df = pd.DataFrame(
        {
            "breed": np.random.choice(breeds, size=n, p=[0.4, 0.3, 0.15, 0.1, 0.05]),
            "color": np.random.choice(colors, size=n, p=[0.5, 0.2, 0.15, 0.1, 0.05]),
            # Precio con distribución desviada para simular drift
            "price": np.random.lognormal(mean=10.5, sigma=0.8, size=n).clip(
                1000, 100000
            ),
        }
    )

    df[cfg.TARGET_COL] = _simulate_labels(n)
    df[cfg.PREDICTION_COL] = _simulate_labels(n)

    return df
