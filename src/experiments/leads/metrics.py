"""
metrics.py
==========
Evaluación, logging MLflow y selección del campeón.
"""

import os
import pickle
import tempfile

import matplotlib.pyplot as plt
import mlflow
import mlflow.xgboost
import numpy as np
from sklearn.metrics import (
    fbeta_score,
)

ORDEN_LEADS = ["Lead Bronce", "Lead Plata", "Lead Oro"]


def predecir_cascada(X, m1, m2) -> np.ndarray:
    pred = np.array(["Lead Bronce"] * len(X), dtype=object)
    mask = m1.predict(X) == 1
    if mask.sum() > 0:
        pred[mask] = np.where(m2.predict(X[mask]) == 1, "Lead Oro", "Lead Plata")
    return pred


def calcular_metricas_cascada(
    p1h,
    p1p,
    p2h,
    p2p,
    X_test_horse,
    X_test_prods,
    y_test,
    X_p2h_raw,
    X_p2p_raw,
    y_p2h_raw,
    y_p2p_raw,
    X_te_horse=None,
    X_te_prods=None,
    y_te=None,
) -> dict:
    _Xh = X_te_horse if X_te_horse is not None else X_test_horse
    _Xp = X_te_prods if X_te_prods is not None else X_test_prods
    _y = y_te if y_te is not None else y_test

    _mask_p2h = _y["horse_target"] != "Lead Bronce"
    _mask_p2p = _y["prods_target"] != "Lead Bronce"
    _y_p2h = (_y["horse_target"][_mask_p2h] == "Lead Oro").astype(int)
    _y_p2p = (_y["prods_target"][_mask_p2p] == "Lead Oro").astype(int)

    _Xp2h_tr = X_p2h_raw[_Xh.columns] if X_te_horse is not None else X_p2h_raw
    _Xp2p_tr = X_p2p_raw[_Xp.columns] if X_te_prods is not None else X_p2p_raw

    metricas = {}
    for tgt, m1_, m2_, y_true, X_dom, X_p2_te, y_p2_te, X_p2_tr, y_p2_tr in [
        (
            "horse",
            p1h,
            p2h,
            _y["horse_target"],
            _Xh,
            _Xh[_mask_p2h],
            _y_p2h,
            _Xp2h_tr,
            y_p2h_raw,
        ),
        (
            "prods",
            p1p,
            p2p,
            _y["prods_target"],
            _Xp,
            _Xp[_mask_p2p],
            _y_p2p,
            _Xp2p_tr,
            y_p2p_raw,
        ),
    ]:
        y_pred = predecir_cascada(X_dom, m1_, m2_)
        f2_macro = fbeta_score(
            y_true, y_pred, beta=2, average="macro", labels=ORDEN_LEADS
        )
        f2_oro = fbeta_score(
            y_true, y_pred, beta=2, labels=["Lead Oro"], average="macro"
        )
        f2_plata = fbeta_score(
            y_true, y_pred, beta=2, labels=["Lead Plata"], average="macro"
        )
        y_pred_p1 = m1_.predict(X_dom)
        y_true_p1 = (y_true != "Lead Bronce").astype(int)
        f2_p1 = fbeta_score(y_true_p1, y_pred_p1, beta=2)
        f2_p2 = fbeta_score(y_p2_te, m2_.predict(X_p2_te), beta=2)
        f2_p2_train = fbeta_score(y_p2_tr, m2_.predict(X_p2_tr), beta=2)
        metricas[tgt] = {
            "f2_macro": f2_macro,
            "f2_lead_oro": f2_oro,
            "f2_lead_plata": f2_plata,
            "f2_paso1": f2_p1,
            "f2_paso2_test": f2_p2,
            "f2_paso2_train": f2_p2_train,
            "overfit_gap_p2": f2_p2_train - f2_p2,
            "y_pred": y_pred,
        }
    return metricas


def loguear_run_mlflow(
    run_name: str,
    model_type: str,
    params_p1: dict,
    params_p2: dict,
    p1h,
    p1p,
    p2h,
    p2p,
    metricas: dict,
    X_train_p1h,
    X_train_p1p,
    X_train_p2h,
    X_train_p2p,
    X_test_horse,
    X_test_prods,
    y_test,
    X_te_horse=None,
    X_te_prods=None,
) -> str:
    _Xte_h = X_te_horse if X_te_horse is not None else X_test_horse
    _Xte_p = X_te_prods if X_te_prods is not None else X_test_prods
    color = "#4C72B0" if model_type == "RandomForest" else "#DD8452"
    _is_xgb = model_type == "XGBoost"

    with mlflow.start_run(run_name=run_name):
        mlflow.set_tag("model_type", model_type)
        mlflow.set_tag("pipeline", "cascada_2pasos_dominio_separado")

        for k, v in params_p1.items():
            mlflow.log_param(f"p1_{k}", v)
        for k, v in params_p2.items():
            mlflow.log_param(f"p2_{k}", v)
        for tgt, m in metricas.items():
            for mn, val in m.items():
                if mn != "y_pred":
                    mlflow.log_metric(f"{mn}_{tgt}", val)

        for nombre_modelo, modelo in [
            ("modelo_p1_horse", p1h),
            ("modelo_p1_prods", p1p),
            ("modelo_p2_horse", p2h),
            ("modelo_p2_prods", p2p),
        ]:
            if _is_xgb:
                mlflow.xgboost.log_model(modelo, artifact_path=nombre_modelo)
            else:
                with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp:
                    pickle.dump(modelo, tmp)
                    mlflow.log_artifact(tmp.name, nombre_modelo)
                    os.unlink(tmp.name)

        fig, axes = plt.subplots(2, 2, figsize=(18, 14))
        for ax, (model, X_ref, label) in zip(
            axes.flatten(),
            [
                (p1h, X_train_p1h, "Paso 1 — horse"),
                (p1p, X_train_p1p, "Paso 1 — prods"),
                (p2h, X_train_p2h, "Paso 2 — horse"),
                (p2p, X_train_p2p, "Paso 2 — prods"),
            ],
        ):
            imp = model.feature_importances_
            n = min(15, len(X_ref.columns))
            idx = np.argsort(imp)[::-1][:n]
            ax.barh(range(n), imp[idx][::-1], color=color)
            ax.set_yticks(range(n))
            ax.set_yticklabels([X_ref.columns[j] for j in idx[::-1]])
            ax.set_title(label)
        _log_fig(fig)

    return mlflow.active_run().info.run_id


def _log_fig(fig):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        fig.savefig(tmp.name, bbox_inches="tight", dpi=100)
        mlflow.log_artifact(tmp.name, "plots")
        os.unlink(tmp.name)
    plt.close(fig)
