"""
metrics.py
==========
Evaluación, logging MLflow y selección del campeón.
"""

import os
import pickle
import tempfile

import numpy as np
import matplotlib.pyplot as plt
import mlflow
import mlflow.xgboost
from sklearn.metrics import (
    fbeta_score, ConfusionMatrixDisplay,
    precision_recall_curve, auc,
)

ORDEN_LEADS = ['Lead Bronce', 'Lead Plata', 'Lead Oro']


# ── Predicción en cascada ─────────────────────────────────────────────────────

def predecir_cascada(X, m1, m2) -> np.ndarray:
    """Paso1 → Paso2 solo sobre quienes pasaron Paso1."""
    pred = np.array(['Lead Bronce'] * len(X), dtype=object)
    mask = m1.predict(X) == 1
    if mask.sum() > 0:
        pred[mask] = np.where(m2.predict(X[mask]) == 1, 'Lead Oro', 'Lead Plata')
    return pred


# ── Métricas completas ────────────────────────────────────────────────────────

def calcular_metricas_cascada(p1h, p1p, p2h, p2p, X_test_horse, X_test_prods, y_test, X_p2h_raw, X_p2p_raw,
                               y_p2h_raw, y_p2p_raw, X_te_horse=None, X_te_prods=None, y_te=None) -> dict:
    """
    Calcula métricas del pipeline para ambos targets.

    X_te_horse / X_te_prods : datasets de evaluación opcionales.
      - Si se omiten: usa X_test_horse / X_test_prods (campeón v1).
      - Si se pasan  : úsalos (p.ej. X_test_horse_v2 para evaluar v2 reducido).
    """
    _Xh = X_te_horse if X_te_horse is not None else X_test_horse
    _Xp = X_te_prods if X_te_prods is not None else X_test_prods
    _y  = y_te       if y_te       is not None else y_test

    _mask_p2h = _y['horse_target'] != 'Lead Bronce'
    _mask_p2p = _y['prods_target'] != 'Lead Bronce'
    _y_p2h    = (_y['horse_target'][_mask_p2h] == 'Lead Oro').astype(int)
    _y_p2p    = (_y['prods_target'][_mask_p2p] == 'Lead Oro').astype(int)

    _Xp2h_tr = X_p2h_raw[_Xh.columns] if X_te_horse is not None else X_p2h_raw
    _Xp2p_tr = X_p2p_raw[_Xp.columns] if X_te_prods is not None else X_p2p_raw

    metricas = {}
    for tgt, m1_, m2_, y_true, X_dom, X_p2_te, y_p2_te, X_p2_tr, y_p2_tr in [
        ('horse', p1h, p2h, _y['horse_target'], _Xh,
         _Xh[_mask_p2h], _y_p2h, _Xp2h_tr, y_p2h_raw),
        ('prods', p1p, p2p, _y['prods_target'], _Xp,
         _Xp[_mask_p2p], _y_p2p, _Xp2p_tr, y_p2p_raw),
    ]:
        y_pred      = predecir_cascada(X_dom, m1_, m2_)
        f2_macro    = fbeta_score(y_true, y_pred, beta=2,
                                  average='macro', labels=ORDEN_LEADS)
        f2_oro      = fbeta_score(y_true, y_pred, beta=2,
                                  labels=['Lead Oro'],   average='macro')
        f2_plata    = fbeta_score(y_true, y_pred, beta=2,
                                  labels=['Lead Plata'], average='macro')
        y_pred_p1   = m1_.predict(X_dom)
        y_true_p1   = (y_true != 'Lead Bronce').astype(int)
        f2_p1       = fbeta_score(y_true_p1, y_pred_p1, beta=2)
        f2_p2       = fbeta_score(y_p2_te, m2_.predict(X_p2_te), beta=2)
        f2_p2_train = fbeta_score(y_p2_tr, m2_.predict(X_p2_tr), beta=2)
        metricas[tgt] = {
            'f2_macro':       f2_macro,
            'f2_lead_oro':    f2_oro,
            'f2_lead_plata':  f2_plata,
            'f2_paso1':       f2_p1,
            'f2_paso2_test':  f2_p2,
            'f2_paso2_train': f2_p2_train,
            'overfit_gap_p2': f2_p2_train - f2_p2,
            'y_pred':         y_pred,
        }
    return metricas


# ── Overfitting ───────────────────────────────────────────────────────────────

def check_overfitting(configs: list, nombre: str):
    print(f'\n  Chequeo Overfitting — {nombre}')
    print('─' * 65)
    print(f'  {"Paso":<18} {"F2 Train":>10} {"F2 Test":>10} {"Gap":>8}  Status')
    print('  ' + '─' * 63)
    for label, model, X_tr, y_tr, X_te, y_te in configs:
        f2_tr  = fbeta_score(y_tr, model.predict(X_tr), beta=2)
        f2_te  = fbeta_score(y_te, model.predict(X_te), beta=2)
        gap    = f2_tr - f2_te
        status = 'OVERFIT' if gap > 0.10 else 'OK'
        print(f'  {label:<18} {f2_tr:>10.4f} {f2_te:>10.4f} {gap:>8.4f}  {status}')


# ── Logging MLflow ────────────────────────────────────────────────────────────

def loguear_run_mlflow(run_name: str, model_type: str, params_p1: dict, params_p2: dict, p1h, p1p, p2h, p2p,
                        metricas: dict, X_train_p1h, X_train_p1p, X_train_p2h, X_train_p2p, X_test_horse, X_test_prods,
                        y_test, X_te_horse=None, X_te_prods=None) -> str:
    """
    Loga params, métricas, modelos y gráficos en MLflow.

    X_te_horse / X_te_prods : datasets de test para los plots.
      Para XGB v2: pasar X_test_horse_v2 / X_test_prods_v2.
    """
    _Xte_h = X_te_horse if X_te_horse is not None else X_test_horse
    _Xte_p = X_te_prods if X_te_prods is not None else X_test_prods
    color   = '#4C72B0' if model_type == 'RandomForest' else '#DD8452'
    _is_xgb = model_type == 'XGBoost'

    with mlflow.start_run(run_name=run_name):
        mlflow.set_tag('model_type',   model_type)
        mlflow.set_tag('pipeline',     'cascada_2pasos_dominio_separado')
        mlflow.set_tag('n_feat_horse', str(X_train_p1h.shape[1]))
        mlflow.set_tag('n_feat_prods', str(X_train_p1p.shape[1]))

        for k, v in params_p1.items():
            mlflow.log_param(f'p1_{k}', v)
        for k, v in params_p2.items():
            mlflow.log_param(f'p2_{k}', v)
        for tgt, m in metricas.items():
            for mn, val in m.items():
                if mn != 'y_pred':
                    mlflow.log_metric(f'{mn}_{tgt}', val)

        for nombre_modelo, modelo in [
            ('modelo_p1_horse', p1h), ('modelo_p1_prods', p1p),
            ('modelo_p2_horse', p2h), ('modelo_p2_prods', p2p),
        ]:
            if _is_xgb:
                mlflow.xgboost.log_model(modelo, artifact_path=nombre_modelo)
            else:
                with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp:
                    pickle.dump(modelo, tmp)
                    mlflow.log_artifact(tmp.name, nombre_modelo)
                    os.unlink(tmp.name)

        # Feature importance
        fig, axes = plt.subplots(2, 2, figsize=(18, 14))
        for ax, (model, X_ref, label) in zip(axes.flatten(), [
            (p1h, X_train_p1h, 'Paso 1 — horse'),
            (p1p, X_train_p1p, 'Paso 1 — prods'),
            (p2h, X_train_p2h, 'Paso 2 — horse'),
            (p2p, X_train_p2p, 'Paso 2 — prods'),
        ]):
            imp = model.feature_importances_
            n   = min(15, len(X_ref.columns))
            idx = np.argsort(imp)[::-1][:n]
            ax.barh(range(n), imp[idx][::-1], color=color)
            ax.set_yticks(range(n))
            ax.set_yticklabels([X_ref.columns[j] for j in idx[::-1]])
            ax.set_title(label)
            ax.set_xlabel('Importancia')
        plt.suptitle(f'Feature Importance — {run_name}', fontsize=13, y=1.01)
        plt.tight_layout()
        _log_fig(fig)

        # Matrices de confusión
        mask_p2h = y_test['horse_target'] != 'Lead Bronce'
        mask_p2p = y_test['prods_target'] != 'Lead Bronce'
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        for ax, (tgt, m1_, m2_, X_dom, y_true) in [
            (axes[0], ('horse_target', p1h, p2h, _Xte_h, y_test['horse_target'])),
            (axes[1], ('prods_target', p1p, p2p, _Xte_p, y_test['prods_target'])),
        ]:
            ConfusionMatrixDisplay.from_predictions(
                y_true, predecir_cascada(X_dom, m1_, m2_),
                labels=ORDEN_LEADS, display_labels=['Bronce', 'Plata', 'Oro'],
                normalize='true', cmap='Blues', ax=ax)
            ax.set_title(f'Confusion Matrix — {tgt}')
        plt.suptitle(run_name, fontsize=12)
        plt.tight_layout()
        _log_fig(fig)

        # Curvas PR
        y_te_p1h = (y_test['horse_target'] != 'Lead Bronce').astype(int)
        y_te_p1p = (y_test['prods_target'] != 'Lead Bronce').astype(int)
        y_te_p2h = (y_test['horse_target'][mask_p2h] == 'Lead Oro').astype(int)
        y_te_p2p = (y_test['prods_target'][mask_p2p] == 'Lead Oro').astype(int)
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        for ax, (model, X_eval, y_true_pr, label) in zip(axes.flatten(), [
            (p1h, _Xte_h,               y_te_p1h, 'P1 horse: Plata/Oro'),
            (p1p, _Xte_p,               y_te_p1p, 'P1 prods: Plata/Oro'),
            (p2h, _Xte_h[mask_p2h],     y_te_p2h, 'P2 horse: Oro'),
            (p2p, _Xte_p[mask_p2p],     y_te_p2p, 'P2 prods: Oro'),
        ]):
            proba        = model.predict_proba(X_eval)[:, 1]
            prec, rec, _ = precision_recall_curve(y_true_pr, proba)
            pr_auc       = auc(rec, prec)
            ax.plot(rec, prec, color=color, lw=2)
            ax.fill_between(rec, prec, alpha=0.1, color=color)
            ax.set_xlabel('Recall')
            ax.set_ylabel('Precision')
            ax.set_title(f'{label}  |  AUC-PR = {pr_auc:.3f}')
            ax.grid(alpha=0.3)
        plt.suptitle(f'Curvas PR — {run_name}', fontsize=13)
        plt.tight_layout()
        _log_fig(fig)

        run_id = mlflow.active_run().info.run_id
        print(f'Run logueado: {run_name}  |  run_id: {run_id}')

    return run_id


def _log_fig(fig):
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        fig.savefig(tmp.name, bbox_inches='tight', dpi=100)
        mlflow.log_artifact(tmp.name, 'plots')
        os.unlink(tmp.name)
    plt.show()
    plt.close(fig)


# ── Selección del campeón ─────────────────────────────────────────────────────

def seleccionar_campeon(experiment_name: str) -> str:
    """
    Busca el run con mayor f2_lead_oro_horse, le asigna tag champion
    y retira el tag del campeón anterior.
    """
    client  = mlflow.tracking.MlflowClient()
    exp     = client.get_experiment_by_name(experiment_name)
    exp_id  = exp.experiment_id

    runs = client.search_runs(
        experiment_ids=[exp_id],
        filter_string='attributes.status = "FINISHED"',
        order_by=['metrics.f2_lead_oro_horse DESC'],
        max_results=10,
    )
    if not runs:
        print('No hay runs finalizados.')
        return None

    for run in runs:
        if run.data.tags.get('status') == 'champion':
            client.set_tag(run.info.run_id, 'status', 'retired')

    mejor  = runs[0]
    nombre = mejor.data.tags.get('mlflow.runName', mejor.info.run_id)
    client.set_tag(mejor.info.run_id, 'status', 'champion')

    m = mejor.data.metrics
    print(f'{"═"*60}')
    print(f' CAMPEÓN: {nombre}')
    print(f'{"═"*60}')
    print(f'  run_id            : {mejor.info.run_id}')
    print(f'  F2 Lead Oro horse : {m.get("f2_lead_oro_horse", float("nan")):.4f}')
    print(f'  F2 Lead Oro prods : {m.get("f2_lead_oro_prods", float("nan")):.4f}')
    print(f'  F2 macro    horse : {m.get("f2_macro_horse",    float("nan")):.4f}')
    print(f'  Gap P2      horse : {m.get("overfit_gap_p2_horse", float("nan")):.4f}')
    print(f'{"─"*60}')
    print(f'  Ranking (F2 Lead Oro horse):')
    print(f'  {"Run":<28} {"F2h":>7} {"F2p":>7} {"Gap":>7}  Status')
    print(f'  {"─"*55}')
    for r in runs:
        rname  = r.data.tags.get('mlflow.runName', r.info.run_id[:8])
        f2h    = r.data.metrics.get('f2_lead_oro_horse',    float('nan'))
        f2p    = r.data.metrics.get('f2_lead_oro_prods',    float('nan'))
        gap    = r.data.metrics.get('overfit_gap_p2_horse', float('nan'))
        status = r.data.tags.get('status', '')
        print(f'  {rname:<28} {f2h:>7.4f} {f2p:>7.4f} {gap:>7.4f}  {status}')

    return mejor.info.run_id
