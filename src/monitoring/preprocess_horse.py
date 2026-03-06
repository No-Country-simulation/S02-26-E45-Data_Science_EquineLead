import pickle
from pathlib import Path

import numpy as np
import pandas as pd

# ── Carga de artefactos ───────────────────────────────────────────────────────


def load_artifacts(outdir: str) -> dict:
    """
    Carga los 5 pkl guardados por save_preprocessing_artifacts().

    Args:
        outdir: directorio con los .pkl  (e.g. "models/champion")

    Returns:
        dict con claves:
            target_encoder, limites_capping, cols_horse, cols_prods, cols_user
    """
    keys = [
        "target_encoder",
        "limites_capping",
        "cols_horse",
        "cols_prods",
        "cols_user",
    ]
    arts = {}
    for key in keys:
        path = Path(outdir) / f"{key}.pkl"
        with open(path, "rb") as f:
            arts[key] = pickle.load(f)
    print(f"✅ Artefactos cargados desde: {outdir}")
    return arts


# ── Preprocesamiento ──────────────────────────────────────────────────────────


def preprocess_horse(df: pd.DataFrame, arts: dict) -> pd.DataFrame:
    """
    Preprocesa un DataFrame crudo y retorna X_horse listo para HORSE_P1.

    Pasos (idénticos a build_datasets de features.py):
        1. Target Encoding sobre columnas categóricas (solo transform)
        2. Capping con límites P99 del entrenamiento
        3. Selección de cols_user + cols_horse

    Args:
        df:   DataFrame con las features crudas (sin columnas target)
        arts: dict retornado por load_artifacts()

    Returns:
        X_horse: DataFrame con exactamente las columnas que espera HORSE_P1
    """
    te = arts["target_encoder"]
    limites_capping = arts["limites_capping"]
    cols_horse = arts["cols_horse"]  # ya incluye cols_user (guardadas así en train)

    X = df.copy()

    # 1. Target Encoding — usar transform(), nunca fit_transform()
    cols_te = [c for c in te.get_feature_names_out() if c in X.columns]
    if cols_te:
        X[cols_te] = te.transform(X[cols_te])

    # 2. Capping
    for col, lim in limites_capping.items():
        if col in X.columns:
            X[col] = X[col].clip(upper=lim)

    # 3. Selección de columnas — rellenar faltantes con 0 y advertir
    missing = [c for c in cols_horse if c not in X.columns]
    if missing:
        print(f"⚠️  Columnas faltantes (se rellenan con 0): {missing}")
        for c in missing:
            X[c] = 0

    return X[cols_horse]


# ── Subset Paso 2 ─────────────────────────────────────────────────────────────


def get_p2_subset(X_horse: pd.DataFrame, pred_p1: np.ndarray | list) -> pd.DataFrame:
    """
    Filtra las filas que HORSE_P1 clasificó como Plata/Oro (pred == 1)
    para pasarlas a HORSE_P2.

    Args:
        X_horse:  DataFrame procesado por preprocess_horse()
        pred_p1:  Predicciones binarias de HORSE_P1 (0=Bronce, 1=Plata/Oro)

    Returns:
        Subset de X_horse donde pred_p1 == 1, listo para HORSE_P2
    """
    mask = pd.Series(pred_p1, index=X_horse.index) == 1
    X_p2 = X_horse[mask]
    print(f"📊 P1 → {mask.sum()} leads potenciales de {len(X_horse)} usuarios")
    return X_p2


# ── Pipeline completo en cascada ──────────────────────────────────────────────


def predict_cascade(
    df: pd.DataFrame,
    arts: dict,
    model_p1,
    model_p2,
) -> pd.DataFrame:
    """
    Pipeline completo: preprocesa + predice en cascada P1 → P2.
    Replica predecir_cascada() de metrics.py con probabilidades incluidas.

    Args:
        df:       DataFrame crudo con features de caballos
        arts:     dict retornado por load_artifacts()
        model_p1: HORSE_P1 ya cargado (XGBClassifier)
        model_p2: HORSE_P2 ya cargado (XGBClassifier)

    Returns:
        DataFrame con columnas:
            pred_p1       — 0=Bronce, 1=Plata/Oro
            pred_p2       — 0=Plata, 1=Oro  (NaN si pred_p1 == 0)
            lead_label    — 'Lead Bronce' | 'Lead Plata' | 'Lead Oro'
            prob_plata_oro — probabilidad Paso 1 (clase positiva)
            prob_oro      — probabilidad Paso 2 (clase positiva, NaN si Bronce)
    """
    X_horse = preprocess_horse(df, arts)

    # Paso 1
    pred_p1 = model_p1.predict(X_horse)
    prob_plata_oro = model_p1.predict_proba(X_horse)[:, 1]

    # Paso 2 — solo sobre no-Bronce
    pred_p2 = np.full(len(X_horse), fill_value=np.nan)
    prob_oro = np.full(len(X_horse), fill_value=np.nan)
    mask = pred_p1 == 1

    if mask.sum() > 0:
        X_p2 = get_p2_subset(X_horse, pred_p1)
        pred_p2[mask] = model_p2.predict(X_p2)
        prob_oro[mask] = model_p2.predict_proba(X_p2)[:, 1]

    # Label final — mismo criterio que predecir_cascada() en metrics.py
    labels = np.where(
        pred_p1 == 0, "Lead Bronce", np.where(pred_p2 == 1, "Lead Oro", "Lead Plata")
    )

    return pd.DataFrame(
        {
            "pred_p1": pred_p1,
            "pred_p2": pred_p2,
            "lead_label": labels,
            "prob_plata_oro": prob_plata_oro,
            "prob_oro": prob_oro,
        },
        index=df.index,
    )
