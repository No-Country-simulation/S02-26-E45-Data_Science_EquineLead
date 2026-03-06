import glob
import os

import cloudpickle
import joblib
import xgboost as xgb

ARTIFACTS_PATH = "./models/production"


def load_model(name: str):
    """
    Carga un modelo desde ARTIFACTS_PATH según su formato:
    - XGBoost  → model.ubj  (formato binario nativo)
    - Sklearn  → model.pkl  (joblib/pickle)
    """
    ubj_path = os.path.join(ARTIFACTS_PATH, name, "model.ubj")
    pkl_path = os.path.join(ARTIFACTS_PATH, name, "model.pkl")

    if os.path.exists(ubj_path):
        model = xgb.XGBClassifier()
        model.load_model(ubj_path)
        return model

    if os.path.exists(pkl_path):
        return joblib.load(pkl_path)

    raise FileNotFoundError(
        f"No se encontró modelo para '{name}'. Se esperaba: {ubj_path} o {pkl_path}"
    )


def load_bundle(name: str) -> dict:
    """
    Carga el artifacts_bundle de un modelo (model, vectorizer, scaler, transform_fn).
    Busca el primer .pkl dentro de ARTIFACTS_PATH/{name}/artifacts_bundle/
    """

    bundle_dir = os.path.join(ARTIFACTS_PATH, name, "artifacts_bundle")
    matches = glob.glob(os.path.join(bundle_dir, "*.pkl"))

    if not matches:
        raise FileNotFoundError(
            f"No se encontró artifacts_bundle para '{name}' en: {bundle_dir}"
        )

    with open(matches[0], "rb") as f:
        return cloudpickle.load(f)
