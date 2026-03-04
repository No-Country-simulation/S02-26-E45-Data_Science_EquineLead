"""
model.py
========
Campeón: XGB Tuneado v1
  run_id : dd6f2989958a48d587e2769933622ff8
  F2 Lead Oro horse : 0.5054
  F2 Lead Oro prods : 0.3605
  F2 macro horse    : 0.7614
  Gap P2 horse      : 0.0266  


Para cambiar el campeón: editar las constantes PARAMS_P1H/P1P/P2H/P2P
y correr train.py. El flag --tune de train.py ejecuta RandomizedSearchCV
para encontrar nuevos mejores params.
"""

import os
import pickle

from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier


# ── Hiperparámetros fijos del campeón ────────────────────────────────────────

PARAMS_XGB_COMUNES = dict(
    eval_metric  = 'aucpr',
    tree_method  = 'hist',
    random_state = 42,
    n_jobs       = -1,
)

# Paso 1 — dominio caballos  
PARAMS_P1H = dict(
    max_depth        = 5,
    learning_rate    = 0.1,
    n_estimators     = 400,
    subsample        = 0.7,
    colsample_bytree = 0.9,
    reg_alpha        = 0.1,
    reg_lambda       = 1.0,
)

# Paso 1 — dominio productos  
PARAMS_P1P = dict(
    max_depth        = 5,
    learning_rate    = 0.1,
    n_estimators     = 200,
    subsample        = 0.7,
    colsample_bytree = 0.9,
    reg_alpha        = 0.1,
    reg_lambda       = 5.0,
)

# Paso 2 — dominio caballos  
PARAMS_P2H = dict(
    max_depth        = 3,
    learning_rate    = 0.1,
    n_estimators     = 200,
    subsample        = 0.7,
    colsample_bytree = 0.7,
    reg_alpha        = 1.0,
    reg_lambda       = 5.0,
)

# Paso 2 — dominio productos  
PARAMS_P2P = dict(
    max_depth        = 5,
    learning_rate    = 0.01,
    n_estimators     = 400,
    subsample        = 0.7,
    colsample_bytree = 0.7,
    reg_alpha        = 1.0,
    reg_lambda       = 5.0,
)


# ── Construcción de modelos ───────────────────────────────────────────────────

def build_p1(X_tr, y_tr, spw: float, params: dict) -> XGBClassifier:
    """
    Paso 1: Bronce (0) vs Plata/Oro (1).
    Usa scale_pos_weight para el desbalance — sin SMOTE en Paso 1.
    Los datos de train ya vienen sin SMOTE (scale_pos_weight maneja el desbalance).
    """
    model = XGBClassifier(**params, **PARAMS_XGB_COMUNES, scale_pos_weight=spw)
    model.fit(X_tr, y_tr)
    return model


def build_p2(X_tr, y_tr, spw: float, params: dict) -> XGBClassifier:
    """
    Paso 2: Plata (0) vs Oro (1).
    Aplica SMOTE antes del fit porque Lead Oro es extremadamente escaso
    """
    X_bal, y_bal = SMOTE(random_state=42).fit_resample(X_tr, y_tr)
    model = XGBClassifier(**params, **PARAMS_XGB_COMUNES, scale_pos_weight=spw)
    model.fit(X_bal, y_bal)
    return model


def build_champion(datasets: dict) -> dict:
    """
    Construye los 4 modelos a partir del dict de build_datasets().

    Retorna dict con:
        p1h, p1p, p2h, p2p         	 	— modelos entrenados
        params_p1h/p1p/p2h/p2p      		— hiperparámetros usados
        spw_p1h/p1p/p2h/p2p         		— scale_pos_weight calculados
        y_tr_p1h/p1p, y_p2h_raw/p2p_raw 	— targets para evaluación posterior
    """
    y_train = datasets['y_train']

    # Targets binarios
    y_tr_p1h  = (y_train['horse_target'] != 'Lead Bronce').astype(int)
    y_tr_p1p  = (y_train['prods_target'] != 'Lead Bronce').astype(int)
    y_p2h_raw = (
        y_train['horse_target'][y_train['horse_target'] != 'Lead Bronce'] == 'Lead Oro'
    ).astype(int)
    y_p2p_raw = (
        y_train['prods_target'][y_train['prods_target'] != 'Lead Bronce'] == 'Lead Oro'
    ).astype(int)

    # scale_pos_weight  (negativos / positivos en train original, sin SMOTE)
    spw_p1h = (y_tr_p1h  == 0).sum() / (y_tr_p1h  == 1).sum()   
    spw_p1p = (y_tr_p1p  == 0).sum() / (y_tr_p1p  == 1).sum()   
    spw_p2h = (y_p2h_raw == 0).sum() / (y_p2h_raw == 1).sum()   
    spw_p2p = (y_p2p_raw == 0).sum() / (y_p2p_raw == 1).sum()

    print(f'scale_pos_weight — P1h:{spw_p1h:.2f}  P1p:{spw_p1p:.2f}  '
          f'P2h:{spw_p2h:.2f}  P2p:{spw_p2p:.2f}')

    print('Entrenando campeón XGB Tuneado...')
    p1h = build_p1(datasets['X_train_horse'], y_tr_p1h,  spw_p1h, PARAMS_P1H)
    print('  OK P1 horse')
    p1p = build_p1(datasets['X_train_prods'], y_tr_p1p,  spw_p1p, PARAMS_P1P)
    print('  OK P1 prods')
    p2h = build_p2(datasets['X_p2h_raw'],     y_p2h_raw, spw_p2h, PARAMS_P2H)
    print('  OK P2 horse  (con SMOTE)')
    p2p = build_p2(datasets['X_p2p_raw'],     y_p2p_raw, spw_p2p, PARAMS_P2P)
    print('  OK P2 prods  (con SMOTE)')

    return dict(
        p1h=p1h, p1p=p1p, p2h=p2h, p2p=p2p,
        params_p1h=PARAMS_P1H, params_p1p=PARAMS_P1P,
        params_p2h=PARAMS_P2H, params_p2p=PARAMS_P2P,
        spw_p1h=spw_p1h, spw_p1p=spw_p1p,
        spw_p2h=spw_p2h, spw_p2p=spw_p2p,
        y_tr_p1h=y_tr_p1h, y_tr_p1p=y_tr_p1p,
        y_p2h_raw=y_p2h_raw, y_p2p_raw=y_p2p_raw,
    )


# ── Guardado / carga ──────────────────────────────────────────────────────────

def save_models(outdir: str, p1h, p1p, p2h, p2p,
                label: str = 'XGB_Tuneado'):
    os.makedirs(outdir, exist_ok=True)
    for nombre, modelo in [
        ('modelo_p1_horse', p1h), ('modelo_p1_prods', p1p),
        ('modelo_p2_horse', p2h), ('modelo_p2_prods', p2p),
    ]:
        path = os.path.join(outdir, f'{nombre}.pkl')
        with open(path, 'wb') as f:
            pickle.dump(modelo, f)
        print(f'  OK {path}')
    print(f'\n  [{label}] → {outdir}/')


def load_models(outdir: str) -> dict:
    names = ['modelo_p1_horse', 'modelo_p1_prods',
             'modelo_p2_horse', 'modelo_p2_prods']
    result = {}
    for name in names:
        with open(os.path.join(outdir, f'{name}.pkl'), 'rb') as f:
            result[name] = pickle.load(f)
    return result
