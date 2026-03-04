"""
train.py
========
Reentrenamiento end-to-end del campeón XGB Tuneado v1.

Uso:
    python train.py --data ../../data/clean/df_final.parquet --outdir ../models/champion

    # Solo tuning de hiperparámetros (luego copiarlos en model.py):
    python train.py --data ../../data/df_final.parquet --tune

Qué cambia en cada archivo si necesitamos actualizar el campeón:
    Hiperparámetros      → model.py  (PARAMS_P1H/P1P/P2H/P2P)
    Features incluidas   → features.py  (COLS_HORSE, COLS_PRODS)
    Features excluidas   → features.py  (COLS_DROP_V2)
    Métricas / plots     → metrics.py
"""

import argparse
import os

import mlflow
import pandas as pd

from features import build_datasets, save_preprocessing_artifacts
from metrics  import (calcular_metricas_cascada, check_overfitting,
                       loguear_run_mlflow, seleccionar_campeon)
from model    import build_champion, save_models, PARAMS_P1H, PARAMS_P1P, PARAMS_P2H, PARAMS_P2P


# ── Configuración MLflow / DagsHub ────────────────────────────────────────────

DAGSHUB_USER    = 'DAGSHUB_USER'
DAGSHUB_REPO    = 'aletbm/S02-26-E45-Data_Science_EquineLead'
EXPERIMENT_NAME = 'EquineLead_LeadScoring'
RUN_NAME        = 'XGB_Tuneado'


def setup_mlflow():
    import getpass
    token = os.environ.get('DAGSHUB_TOKEN') or getpass.getpass('DagsHub token: ')
    os.environ['MLFLOW_TRACKING_USERNAME'] = DAGSHUB_USER
    os.environ['MLFLOW_TRACKING_PASSWORD'] = token
    mlflow.set_tracking_uri(f'https://dagshub.com/{DAGSHUB_REPO}.mlflow')
    mlflow.set_experiment(EXPERIMENT_NAME)
    print(f'MLflow → experimento: {EXPERIMENT_NAME}')


# ── Pipeline principal ────────────────────────────────────────────────────────

def train(data_path: str, outdir: str):

    # 1. Carga
    print(f'\n[1/6] Cargando {data_path}...')
    if data_path.endswith('.parquet'):
        df_final = pd.read_parquet(data_path)
    else:
        df_final = pd.read_csv(data_path)
    print(f'      {df_final.shape[0]:,} filas × {df_final.shape[1]} cols')

    # 2. Preprocesamiento
    print('\n[2/6] Preprocesamiento...')
    datasets = build_datasets(df_final)
    y_train  = datasets['y_train']
    y_test   = datasets['y_test']

    # Masks y targets auxiliares para evaluación
    mask_test_p2_horse = y_test['horse_target'] != 'Lead Bronce'
    mask_test_p2_prods = y_test['prods_target'] != 'Lead Bronce'
    y_test_p1_horse    = (y_test['horse_target'] != 'Lead Bronce').astype(int)
    y_test_p1_prods    = (y_test['prods_target'] != 'Lead Bronce').astype(int)
    y_test_p2_horse    = (y_test['horse_target'][mask_test_p2_horse] == 'Lead Oro').astype(int)
    y_test_p2_prods    = (y_test['prods_target'][mask_test_p2_prods] == 'Lead Oro').astype(int)

    # 3. Entrenamiento
    print('\n[3/6] Entrenando...')
    models = build_champion(datasets)
    p1h, p1p = models['p1h'], models['p1p']
    p2h, p2p = models['p2h'], models['p2p']

    # 4. Evaluación
    print('\n[4/6] Evaluando...')
    metricas = calcular_metricas_cascada(
        p1h=p1h, p1p=p1p, p2h=p2h, p2p=p2p,
        X_test_horse = datasets['X_test_horse'],
        X_test_prods = datasets['X_test_prods'],
        y_test       = y_test,
        X_p2h_raw    = datasets['X_p2h_raw'],
        X_p2p_raw    = datasets['X_p2p_raw'],
        y_p2h_raw    = models['y_p2h_raw'],
        y_p2p_raw    = models['y_p2p_raw'],
    )
    for tgt, m in metricas.items():
        print(f'  {tgt}: F2 macro={m["f2_macro"]:.4f} | '
              f'F2 Oro={m["f2_lead_oro"]:.4f} | Gap P2={m["overfit_gap_p2"]:.4f}')

    check_overfitting([
        ('P1 — horse', p1h, datasets['X_train_horse'], models['y_tr_p1h'],
         datasets['X_test_horse'], y_test_p1_horse),
        ('P1 — prods', p1p, datasets['X_train_prods'], models['y_tr_p1p'],
         datasets['X_test_prods'], y_test_p1_prods),
        ('P2 — horse', p2h, datasets['X_p2h_raw'], models['y_p2h_raw'],
         datasets['X_test_horse'][mask_test_p2_horse], y_test_p2_horse),
        ('P2 — prods', p2p, datasets['X_p2p_raw'], models['y_p2p_raw'],
         datasets['X_test_prods'][mask_test_p2_prods], y_test_p2_prods),
    ], RUN_NAME)

    # 5. Logging MLflow
    print('\n[5/6] Logueando en MLflow...')
    setup_mlflow()
    run_id = loguear_run_mlflow(
        run_name    = RUN_NAME,
        model_type  = 'XGBoost',
        params_p1   = {**PARAMS_P1H, 'scale_pos_weight': models['spw_p1h']},
        params_p2   = {**PARAMS_P2H, 'scale_pos_weight': models['spw_p2h']},
        p1h=p1h, p1p=p1p, p2h=p2h, p2p=p2p,
        metricas    = metricas,
        X_train_p1h = datasets['X_train_horse'],
        X_train_p1p = datasets['X_train_prods'],
        X_train_p2h = datasets['X_p2h_raw'],
        X_train_p2p = datasets['X_p2p_raw'],
        X_test_horse = datasets['X_test_horse'],
        X_test_prods = datasets['X_test_prods'],
        y_test       = y_test,
        # X_te_horse / X_te_prods se omiten → usa los globales (v1 sin reducción)
    )
    seleccionar_campeon(EXPERIMENT_NAME)

    # 6. Guardado local
    print(f'\n[6/6] Guardando en {outdir}...')
    save_models(outdir, p1h, p1p, p2h, p2p, label=RUN_NAME)
    save_preprocessing_artifacts(
        outdir          = outdir,
        te              = datasets['te'],
        limites_capping = datasets['limites_capping'],
        cols_horse      = datasets['cols_horse'],
        cols_prods      = datasets['cols_prods'],
    )

    print(f'\n✓ Listo.')
    print(f'  run_id        : {run_id}')
    print(f'  F2 Oro horse  : {metricas["horse"]["f2_lead_oro"]:.4f}')
    print(f'  F2 Oro prods  : {metricas["prods"]["f2_lead_oro"]:.4f}')
    return run_id, metricas


# ── Tuning de hiperparámetros (opcional) ─────────────────────────────────────

def tune(data_path: str):
    """
    Corre RandomizedSearchCV en los 4 modelos y muestra los mejores params.
    Copiarlos en model.py (PARAMS_P1H/P1P/P2H/P2P) antes de reentrenar.
    """
    from imblearn.pipeline import Pipeline as ImbPipeline
    from imblearn.over_sampling import SMOTE
    from sklearn.metrics import fbeta_score, make_scorer
    from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
    from xgboost import XGBClassifier
    from model import PARAMS_XGB_COMUNES

    print(f'\n[TUNE] Cargando {data_path}...')
    df_final = pd.read_parquet(data_path) if data_path.endswith('.parquet') \
               else pd.read_csv(data_path)
    datasets = build_datasets(df_final)
    y_train  = datasets['y_train']

    y_tr_p1h  = (y_train['horse_target'] != 'Lead Bronce').astype(int)
    y_tr_p1p  = (y_train['prods_target'] != 'Lead Bronce').astype(int)
    y_p2h_raw = (y_train['horse_target'][y_train['horse_target'] != 'Lead Bronce'] == 'Lead Oro').astype(int)
    y_p2p_raw = (y_train['prods_target'][y_train['prods_target'] != 'Lead Bronce'] == 'Lead Oro').astype(int)

    spw_p1h = (y_tr_p1h  == 0).sum() / (y_tr_p1h  == 1).sum()
    spw_p1p = (y_tr_p1p  == 0).sum() / (y_tr_p1p  == 1).sum()
    spw_p2h = (y_p2h_raw == 0).sum() / (y_p2h_raw == 1).sum()
    spw_p2p = (y_p2p_raw == 0).sum() / (y_p2p_raw == 1).sum()

    f2_scorer  = make_scorer(fbeta_score, beta=2)
    cv3        = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    param_dist = {
        'max_depth':        [3, 4, 5],
        'learning_rate':    [0.01, 0.05, 0.1],
        'n_estimators':     [200, 400],
        'subsample':        [0.7, 0.9],
        'colsample_bytree': [0.7, 0.9],
        'reg_alpha':        [0, 0.1, 1.0],
        'reg_lambda':       [1.0, 5.0],
    }

    def _p1(X_tr, y_tr, spw, label):
        rs = RandomizedSearchCV(
            XGBClassifier(scale_pos_weight=spw, **PARAMS_XGB_COMUNES),
            param_dist, n_iter=15, scoring=f2_scorer,
            cv=cv3, n_jobs=-1, verbose=0, random_state=42,
        )
        rs.fit(X_tr, y_tr)
        print(f'  {label}: {rs.best_params_}  CV F2={rs.best_score_:.4f}')
        return rs.best_params_

    def _p2(X_tr, y_tr, spw, label):
        pd2 = {f'xgb__{k}': v for k, v in param_dist.items()}
        pipe = ImbPipeline([
            ('smote', SMOTE(random_state=42)),
            ('xgb',   XGBClassifier(scale_pos_weight=spw, **PARAMS_XGB_COMUNES)),
        ])
        rs = RandomizedSearchCV(pipe, pd2, n_iter=15, scoring=f2_scorer,
                                cv=cv3, n_jobs=-1, verbose=0, random_state=42)
        rs.fit(X_tr, y_tr)
        best = {k.replace('xgb__', ''): v for k, v in rs.best_params_.items()}
        print(f'  {label}: {best}  CV F2={rs.best_score_:.4f}')
        return best

    print('\n── Paso 1 ──')
    bp1h = _p1(datasets['X_train_horse'], y_tr_p1h,  spw_p1h, 'P1 horse')
    bp1p = _p1(datasets['X_train_prods'], y_tr_p1p,  spw_p1p, 'P1 prods')
    print('\n── Paso 2 ──')
    bp2h = _p2(datasets['X_p2h_raw'],     y_p2h_raw, spw_p2h, 'P2 horse')
    bp2p = _p2(datasets['X_p2p_raw'],     y_p2p_raw, spw_p2p, 'P2 prods')

    print('\n── Copiá esto en model.py ──')
    for label, params in [('PARAMS_P1H', bp1h), ('PARAMS_P1P', bp1p),
                           ('PARAMS_P2H', bp2h), ('PARAMS_P2P', bp2p)]:
        print(f'{label} = {params}')


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reentrenar campeón XGB Tuneado')
    parser.add_argument('--data',   required=True,
                        help='Ruta al df_final (.parquet o .csv)')
    parser.add_argument('--outdir', default='../../models/champion',
                        help='Directorio de salida de modelos y artefactos')
    parser.add_argument('--tune',   action='store_true',
                        help='Ejecutar tuning antes de entrenar')
    args = parser.parse_args()

    print('=' * 60)
    print(' Lead Scoring — XGB Tuneado v1')
    print('=' * 60)

    if args.tune:
        tune(args.data)
        print('\nActualizá PARAMS_* en model.py y corré sin --tune.')
    else:
        train(data_path=args.data, outdir=args.outdir)
