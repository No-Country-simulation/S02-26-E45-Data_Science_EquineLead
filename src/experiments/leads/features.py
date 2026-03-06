"""
features.py
===========
Definición de features por dominio, Target Encoding, capping y
construcción de los datasets de entrenamiento / test.

Campeón: XGB Tuneado v1 (27 features horse, 22 features prods)
  — El XGB v2 reducido fue descartado: Δ F2 Oro horse = -0.0478 (< umbral -0.01)
"""

import pickle

import pandas as pd
from category_encoders import TargetEncoder
from sklearn.model_selection import train_test_split

# ── 1. Columnas con Target Encoding ──────────────────────────────────────────

COLS_TARGET_ENCODE = [
    "user_region",
    "user_card_issuer",
    "user_domain",
    "gender_mode",
    "breed_family_mode",
    "color_mode",  # presentes si el FE las genera
    "most_viewed_category",
    "most_viewed_brand",
    "most_viewed_target_user",
]


# ── Features eliminadas (COLS_DROP_V2) ────────────────────────────────────

COLS_DROP_ZERO_VAR = [
    "unique_regions_horses",
    "prestige_gap",
    "has_both_interests",
]

COLS_DROP_COLINEALES = [
    "total_views",
    "total_cart_adds",
    "ratio_cart_global",
    "avg_horse_price_viewed",
    "min_horse_price_viewed",
    "max_visitas_mismo_producto",
]

COLS_DROP_LOW_SIGNAL = [
    "avg_horse_age",
    "avg_prestige_score_horses",
    "avg_prestige_score_products",
    "avg_height",
    "avg_weight",
    "has_registry_viewed",
    "avg_tech_score",
    "avg_temperament",
    "avg_comment_length",
    "avg_product_price_viewed",
    "ratio_horse_views",
]

COLS_DROP_V2 = COLS_DROP_ZERO_VAR + COLS_DROP_COLINEALES + COLS_DROP_LOW_SIGNAL


# ── 3. Features por dominio del campeón (v1 — sin reducción) ─────────────────

COLS_USER = [
    "user_prestige_score",
    "user_antiguedad_dias",
    "user_region",
    "user_card_issuer",
    "user_domain",
]

COLS_HORSE = [
    "horses_viewed",
    "horses_added_to_cart",
    "max_horse_price_viewed",
    "viewed_premium_horses",
    "viewed_sport_elite",
    "viewed_family_safe",
    "viewed_working_elite",
    "viewed_pro_sellers",
    "has_shipping_viewed",
    "caballos_unicos_vistos",
    "ratio_recurrencia_horse",
    "max_visitas_mismo_caballo",
    "ratio_cart_horse",
    "rango_precio_horse",
    "gender_mode",
    "breed_family_mode",
    "color_mode",
    "avg_horse_age",
    "avg_prestige_score_horses",
    "avg_height",
    "avg_weight",
    "has_registry_viewed",
    "avg_tech_score",
    "avg_temperament",
    "avg_comment_length",
]

COLS_PRODS = [
    "products_viewed",
    "products_added_to_cart",
    "max_product_price_viewed",
    "unique_categories",
    "viewed_waterproof",
    "viewed_leather",
    "viewed_breathable",
    "viewed_uv_protection",
    "viewed_machine_washable",
    "productos_unicos_vistos",
    "ratio_recurrencia_prods",
    "ratio_cart_prods",
    "most_viewed_category",
    "most_viewed_brand",
    "most_viewed_target_user",
    "avg_prestige_score_products",
    "avg_product_price_viewed",
]


# ── 4. Capping ────────────────────────────────────────────────────────────────

COLS_CAPPING_FIJAS = ["max_horse_price_viewed", "viewed_sport_elite"]


def compute_capping_limits(X_train: pd.DataFrame) -> dict:
    """Calcula límites P99 sobre X_train. Solo usar datos de train (no leakage)."""
    cols_auto = [
        col
        for col in X_train.select_dtypes(include="number").columns
        if (p99 := X_train[col].quantile(0.99)) > 0 and X_train[col].max() / p99 > 2
    ]
    cols = list(set(COLS_CAPPING_FIJAS + cols_auto))
    return {col: X_train[col].quantile(0.99) for col in cols if col in X_train.columns}


def apply_capping(X: pd.DataFrame, limites: dict) -> pd.DataFrame:
    X = X.copy()
    for col, lim in limites.items():
        if col in X.columns:
            X[col] = X[col].clip(upper=lim)
    return X


# ── 5. Pipeline completo ──────────────────────────────────────────────────────


def build_datasets(df_final: pd.DataFrame) -> dict:
    X = df_final.drop(columns=["horse_target", "prods_target"])
    y = df_final[["horse_target", "prods_target"]]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y, test_size=0.2, random_state=42
    )

    target_ord = y_train["horse_target"].map(
        {"Lead Bronce": 0, "Lead Plata": 1, "Lead Oro": 2}
    )
    cols_te = [c for c in COLS_TARGET_ENCODE if c in X_train.columns]
    te = TargetEncoder(cols=cols_te, smoothing=10)
    X_train[cols_te] = te.fit_transform(X_train[cols_te], target_ord)
    X_test[cols_te] = te.transform(X_test[cols_te])

    limites_capping = compute_capping_limits(X_train)
    X_train = apply_capping(X_train, limites_capping)
    X_test = apply_capping(X_test, limites_capping)

    cols_user = [c for c in COLS_USER if c in X_train.columns]
    cols_horse = [c for c in COLS_HORSE if c in X_train.columns]
    cols_prods = [c for c in COLS_PRODS if c in X_train.columns]

    X_train_horse = X_train[cols_user + cols_horse]
    X_test_horse = X_test[cols_user + cols_horse]
    X_train_prods = X_train[cols_user + cols_prods]
    X_test_prods = X_test[cols_user + cols_prods]

    mask_p2_horse = y_train["horse_target"] != "Lead Bronce"
    mask_p2_prods = y_train["prods_target"] != "Lead Bronce"
    X_p2h_raw = X_train_horse[mask_p2_horse]
    X_p2p_raw = X_train_prods[mask_p2_prods]

    return dict(
        X_train_horse=X_train_horse,
        X_test_horse=X_test_horse,
        X_train_prods=X_train_prods,
        X_test_prods=X_test_prods,
        X_p2h_raw=X_p2h_raw,
        X_p2p_raw=X_p2p_raw,
        y_train=y_train,
        y_test=y_test,
        te=te,
        limites_capping=limites_capping,
        cols_horse=list(X_train_horse.columns),
        cols_prods=list(X_train_prods.columns),
    )


# ── 6. Serialización ──────────────────────────────────────────────────────────


def save_preprocessing_artifacts(
    outdir: str, te, limites_capping: dict, cols_horse: list, cols_prods: list
):
    import os

    os.makedirs(outdir, exist_ok=True)
    artifacts = {
        "target_encoder.pkl": te,
        "limites_capping.pkl": limites_capping,
        "cols_horse.pkl": cols_horse,
        "cols_prods.pkl": cols_prods,
        "cols_user.pkl": COLS_USER,
    }
    for fname, obj in artifacts.items():
        path = os.path.join(outdir, fname)
        with open(path, "wb") as f:
            pickle.dump(obj, f)


def load_preprocessing_artifacts(outdir: str) -> dict:
    keys = [
        "target_encoder",
        "limites_capping",
        "cols_horse",
        "cols_prods",
        "cols_user",
    ]
    result = {}
    for key in keys:
        with open(f"{outdir}/{key}.pkl", "rb") as f:
            result[key] = pickle.load(f)
    return result
