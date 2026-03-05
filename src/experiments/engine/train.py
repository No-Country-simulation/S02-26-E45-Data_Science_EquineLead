import sys
import io
import tempfile
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from misc.config import init_mlflow, start_run, SEED, MLFLOW_EXPERIMENT_ENGINE_NAME
from misc.utils import load_dataset, log_dataset_metadata
import mlflow
import cloudpickle
import numpy as np
import pandas as pd
from features import build_features
from scipy.sparse import hstack
from model import train_model
from metrics import evaluate
import platform
import datetime

PATH_DATA = Path("./data/clean")
DATASET_NAME = "horses_listings_limpio.parquet"

# ==================================
# DATA SCIENTIST PERSONAL CONFIG
# ==================================
RUN_NAME = f"knn_cosine_recommender_{datetime.datetime.now():%Y%m%d_%H%M%S}"
DS_NAME = "Daisy Quinteros Silva"
STAGE = "training"


def transform_input(data, tfidf, scaler):
    """
    Definida inline en train.py para que cloudpickle serialice el bytecode
    sin referenciar el módulo `features`, que no existe en el contenedor API.
    """
    df = pd.DataFrame([data]) if isinstance(data, dict) else data.copy()
    df.columns = [c.lower().strip() for c in df.columns]
    df["caracteristicas"] = (
        df["breed"].fillna("desconocido") + " " + df["color"].fillna("desconocido")
    ).str.lower()
    matrix_text = tfidf.transform(df["caracteristicas"])
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
    price_scaled = scaler.transform(df[["price"]])
    return hstack([matrix_text, price_scaled]).tocsr()


def main():
    init_mlflow(experiment_name=MLFLOW_EXPERIMENT_ENGINE_NAME)
    with start_run(run_name=RUN_NAME, ds_name=DS_NAME, stage=STAGE):
        # =====================
        # Load dataset
        # =====================
        df = load_dataset(path=PATH_DATA / DATASET_NAME)

        # =====================
        # Feature Engineering
        # =====================
        X_train, X_val, y_train, y_val, tfidf, scaler = build_features(
            df=df, random_state=SEED
        )

        # =====================
        # Train
        # =====================
        model = train_model(X_train, y_train, random_state=SEED)

        # =====================
        # Evaluate
        # =====================
        metrics = evaluate(model, X_val, y_val)
        for k, v in metrics.items():
            mlflow.log_metric(k, v)

        # =====================
        # Dataset version
        # =====================
        log_dataset_metadata(
            name="horses_listings",
            version="v1.0.2",
            path=f"/clean/{DATASET_NAME}",
            n_rows=df.shape[0],
            n_cols=df.shape[1],
        )

        # =====================
        # Reproducibility
        # =====================
        mlflow.log_param("random_state", SEED)

        # =====================
        # Environment
        # =====================
        mlflow.log_param("python_version", sys.version)
        mlflow.log_param("os", platform.system())

        # =====================
        # Model Info
        # =====================
        mlflow.log_param("model_type", model.__class__.__name__)
        mlflow.log_param("metric", "cosine")
        mlflow.log_param("n_neighbors", 5)
        mlflow.log_param("features_used", "price, breed, color")
        mlflow.log_param("vectorizer_type", "TfidfVectorizer")
        mlflow.log_param("scaler_type", "MinMaxScaler")

        # =====================
        # Input example
        # =====================
        input_example = pd.DataFrame(
            [
                {
                    "breed": (
                        df["breed"].mode()[0]
                        if "breed" in df.columns
                        else "desconocido"
                    ),
                    "color": (
                        df["color"].mode()[0]
                        if "color" in df.columns
                        else "desconocido"
                    ),
                    "price": (
                        float(df["price"].median()) if "price" in df.columns else 0.0
                    ),
                }
            ]
        )

        X_example = transform_input(input_example, tfidf, scaler)

        # =====================
        # Artifacts
        # =====================

        # 1. Modelo registrado con input_example y signature inferida
        signature = mlflow.models.infer_signature(
            model_input=X_example,
            model_output=np.array([[0.0] * 5]),
        )

        mlflow.sklearn.log_model(
            model,
            artifact_path="model_engine",
            input_example=X_example,
            signature=signature,
        )

        mlflow.set_tag("status", "champion")

        # 2. Bundle completo para la API
        artifacts_bundle = {
            "model": model,
            "vectorizer": tfidf,
            "scaler": scaler,
            "input_schema": {
                "breed": "str  — raza del caballo (e.g. 'Thoroughbred')",
                "color": "str  — color del pelaje (e.g. 'bay')",
                "price": "float — precio de referencia en USD",
            },
            "transform_fn": transform_input,  # bytecode completo, sin referencia a módulo externo
        }

        tmp_dir = Path(tempfile.mkdtemp())
        bundle_path = tmp_dir / "artifacts_bundle.pkl"
        try:
            with open(bundle_path, "wb") as f:
                cloudpickle.dump(artifacts_bundle, f)
            mlflow.log_artifact(str(bundle_path), artifact_path="artifacts_bundle")
        finally:
            bundle_path.unlink(missing_ok=True)
            tmp_dir.rmdir()

        # 3. Input example como CSV en memoria
        csv_buffer = io.StringIO()
        input_example.to_csv(csv_buffer, index=False)
        mlflow.log_text(
            csv_buffer.getvalue(), artifact_file="artifacts_bundle/input_example.csv"
        )


if __name__ == "__main__":
    main()
