import os
import pickle
from pathlib import Path

import config as cfg
import numpy as np
import pandas as pd
from preprocess_horse import load_artifacts, predict_cascade


def load_models(outdir: str) -> dict:
    names = ["modelo_p1_horse", "modelo_p1_prods", "modelo_p2_horse", "modelo_p2_prods"]
    result = {}
    for name in names:
        with open(os.path.join(outdir, f"{name}.pkl"), "rb") as f:
            result[name] = pickle.load(f)
    return result


def _load_raw(path: str) -> pd.DataFrame:
    p = Path(path)
    if p.suffix == ".parquet":
        return pd.read_parquet(p)
    elif p.suffix == ".csv":
        return pd.read_csv(p)
    else:
        raise ValueError(f"Formato no soportado: {p.suffix}")


def _add_predictions(df_raw: pd.DataFrame, arts: dict, models: dict) -> pd.DataFrame:
    """
    Corre el pipeline de inferencia sobre datos crudos y agrega:
        - lead_label    → ground truth simulado desde horse_target
        - prediction    → label predicho por la cascada P1 → P2
        - prob_plata_oro, prob_oro → probabilidades
    """
    # Separar target si viene en los datos (como en entrenamiento)
    df_features = df_raw.drop(
        columns=[c for c in ["horse_target", "prods_target"] if c in df_raw.columns]
    )

    # Correr cascada
    result = predict_cascade(
        df_features,
        arts,
        models["modelo_p1_horse"],
        models["modelo_p2_horse"],
    )

    # Ground truth — usar horse_target si existe, si no simular
    if "horse_target" in df_raw.columns:
        result[cfg.TARGET_COL] = df_raw["horse_target"].values
    else:
        print("⚠️  Sin ground truth — simulando labels.")
        result[cfg.TARGET_COL] = np.random.choice(
            ["Lead Bronce", "Lead Plata", "Lead Oro"],
            size=len(result),
            p=[0.6, 0.3, 0.1],
        )

    result[cfg.PREDICTION_COL] = result["lead_label"]
    return result


def load_reference_data() -> pd.DataFrame:
    """Carga el dataset de entrenamiento como referencia."""
    arts = load_artifacts(cfg.ARTIFACTS_DIR)
    models = load_models(cfg.MODELS_DIR)

    df_raw = _load_raw(cfg.REFERENCE_DATA_PATH)
    print(f"✅ Reference data: {len(df_raw)} filas")
    return _add_predictions(df_raw, arts, models)


def load_current_data() -> pd.DataFrame:
    """
    Carga los datos de producción.

    Si CURRENT_DATA_PATH no existe → genera datos sintéticos como fallback.
    Reemplazá el archivo en CURRENT_DATA_PATH con tus logs reales.
    """
    path = Path(cfg.CURRENT_DATA_PATH)

    if not path.exists():
        print(f"⚠️  {path} no encontrado — usando datos sintéticos.")
        return _generate_synthetic_data()

    arts = load_artifacts(cfg.ARTIFACTS_DIR)
    models = load_models(cfg.MODELS_DIR)

    df_raw = _load_raw(str(path))
    print(f"✅ Current data: {len(df_raw)} filas")
    return _add_predictions(df_raw, arts, models)


def _generate_synthetic_data(n: int = 500) -> pd.DataFrame:
    """
    Fallback — genera datos sintéticos con distribución levemente desviada
    para simular drift. Reemplazar con logs reales cuando estén disponibles.
    """
    print("🔧 Generando datos sintéticos de producción...")
    np.random.seed(99)
    df = pd.DataFrame(
        {
            "horses_viewed": np.random.poisson(5, n),
            "horses_added_to_cart": np.random.poisson(1, n),
            "max_horse_price_viewed": np.random.lognormal(10, 1, n).clip(0, 500_000),
            "viewed_premium_horses": np.random.poisson(1, n),
            "viewed_sport_elite": np.random.poisson(0.5, n),
            "viewed_family_safe": np.random.poisson(1, n),
            "viewed_working_elite": np.random.poisson(0.5, n),
            "viewed_pro_sellers": np.random.poisson(2, n),
            "has_shipping_viewed": np.random.randint(0, 2, n),
            "caballos_unicos_vistos": np.random.poisson(3, n),
            "ratio_recurrencia_horse": np.random.uniform(0, 1, n),
            "max_visitas_mismo_caballo": np.random.poisson(2, n),
            "ratio_cart_horse": np.random.uniform(0, 0.5, n),
            "rango_precio_horse": np.random.randint(0, 5, n),
            "user_prestige_score": np.random.randint(0, 100, n),
            "user_antiguedad_dias": np.random.randint(0, 1000, n),
            "user_region": np.random.choice(["norte", "sur", "centro"], n),
            "user_card_issuer": np.random.choice(["visa", "mastercard", "amex"], n),
            "user_domain": np.random.choice(["gmail", "hotmail", "yahoo"], n),
            cfg.TARGET_COL: np.random.choice(
                ["Lead Bronce", "Lead Plata", "Lead Oro"], n, p=[0.6, 0.3, 0.1]
            ),
            cfg.PREDICTION_COL: np.random.choice(
                ["Lead Bronce", "Lead Plata", "Lead Oro"], n, p=[0.55, 0.32, 0.13]
            ),
        }
    )
    return df
