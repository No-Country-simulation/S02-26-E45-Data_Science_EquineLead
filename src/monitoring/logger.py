"""
Logger de predicciones para integración con Gradio.

USO EN LA APP GRADIO:
---------------------
from monitoring.prediction_logger import log_prediction

# Dentro de la función de predicción de Gradio:
log_prediction(
    breed="andalusian",
    color="bay",
    price=22000.0,
    neighbors=[142, 87, 210, 55, 301],
    distances=[0.0, 0.14, 0.21, 0.30, 0.35],
    label=None,  # ground truth — None si no está disponible
)

Los logs se acumulan en CURRENT_DATA_PATH y son consumidos por el monitoring_flow.
"""

import csv
from datetime import datetime
from pathlib import Path

import config as cfg

LOG_PATH = Path(cfg.CURRENT_DATA_PATH).with_suffix(".csv")
LOG_FIELDS = [
    "timestamp",
    "breed",
    "color",
    "price",
    "top_neighbor_index",
    "top_distance",
    cfg.PREDICTION_COL,
    cfg.TARGET_COL,
]


def _ensure_log_file():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists():
        with open(LOG_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
            writer.writeheader()


def log_prediction(
    breed: str,
    color: str,
    price: float,
    neighbors: list[int],
    distances: list[float],
    label: int | None = None,
):
    """
    Loguea una predicción del modelo a CSV.

    Args:
        breed:      Raza del caballo
        color:      Color del pelaje
        price:      Precio de referencia
        neighbors:  Índices de los vecinos más cercanos
        distances:  Distancias coseno correspondientes
        label:      Ground truth (0/1). None si no está disponible → se simula.
    """
    import random

    _ensure_log_file()

    # Si no hay ground truth, simular
    # (reemplazar con lógica real cuando esté disponible)
    if label is None:
        label = random.choices([0, 1], weights=[0.7, 0.3])[0]

    # Predicción binaria basada en distancia del vecino más cercano
    prediction = 1 if (distances[0] < 0.2) else 0

    row = {
        "timestamp": datetime.now().isoformat(),
        "breed": breed,
        "color": color,
        "price": price,
        "top_neighbor_index": neighbors[0] if neighbors else None,
        "top_distance": round(distances[0], 4) if distances else None,
        cfg.PREDICTION_COL: prediction,
        cfg.TARGET_COL: label,
    }

    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        writer.writerow(row)
