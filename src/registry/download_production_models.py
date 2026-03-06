import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import os

import mlflow

from misc.config import init_mlflow

init_mlflow()

client = mlflow.tracking.MlflowClient()

REGISTERED_MODELS = [
    "model_engine",
    "HORSE_P1",
    "HORSE_P2",
    "PRODS_P1",
    "PRODS_P2",
]

# Modelos que tienen artifacts_bundle (vectorizer, scaler, transform_fn)
MODELS_WITH_BUNDLE = {"model_engine"}


def download_production_model(model_name: str, dst_path: str = "./models/production/"):
    """Descarga el modelo con alias 'production' del registry"""

    # Obtener la versión en production
    try:
        model_version = client.get_model_version_by_alias(model_name, "production")
    except Exception as e:
        print(f"❌ {model_name} no tiene versión en production: {e}")
        return None

    version = model_version.version
    run_id = model_version.run_id
    print(f"\n📦 {model_name} v{version} (run_id: {run_id})")

    # Descargar el modelo directo desde el registry
    model_uri = f"models:/{model_name}@production"
    local_path = os.path.join(dst_path, model_name)
    os.makedirs(local_path, exist_ok=True)

    mlflow.artifacts.download_artifacts(
        artifact_uri=model_uri,
        dst_path=local_path,
    )
    print(f"✅ {model_name} descargado en: {local_path}")

    # Descargar artifacts_bundle si el modelo lo tiene
    if model_name in MODELS_WITH_BUNDLE:
        try:
            bundle_uri = f"runs:/{run_id}/artifacts_bundle"
            mlflow.artifacts.download_artifacts(
                artifact_uri=bundle_uri,
                dst_path=local_path,
            )
            print(f"✅ artifacts_bundle descargado en: {local_path}")
        except Exception as e:
            print(f"⚠️  {model_name} no tiene artifacts_bundle: {e}")

    return local_path


def download_all_production_models(dst_path: str = "./models/production/"):
    """Descarga todos los modelos en production"""
    paths = {}
    for model_name in REGISTERED_MODELS:
        path = download_production_model(model_name, dst_path=dst_path)
        if path:
            paths[model_name] = path

    print(f"\n✅ {len(paths)}/{len(REGISTERED_MODELS)} modelos descargados")
    return paths


if __name__ == "__main__":
    # Descargar todos los modelos en production
    paths = download_all_production_models()
