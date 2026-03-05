import sys
import io
import tempfile
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from misc.config import init_mlflow, start_run, SEED, MLFLOW_EXPERIMENT_ENGINE_NAME
from misc.utils import load_dataset, log_dataset_metadata
import mlflow
import joblib
import numpy as np
import pandas as pd
from features import build_features, transform_input
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
        # Representa un caballo típico de los datos de entrenamiento.
        # Se usa para documentar el esquema esperado en la API y en MLflow.
        # =====================
        input_example = pd.DataFrame([{
            "breed": df["breed"].mode()[0] if "breed" in df.columns else "desconocido",
            "color": df["color"].mode()[0] if "color" in df.columns else "desconocido",
            "price": float(df["price"].median()) if "price" in df.columns else 0.0,
        }])

        # Transformar el ejemplo para validar que el pipeline funciona end-to-end
        X_example = transform_input(input_example, tfidf, scaler)

        # =====================
        # Artifacts
        # =====================

        # 1. Modelo registrado con input_example y signature inferida
        signature = mlflow.models.infer_signature(
            model_input=X_example,          # sparse CSR → numpy array internamente
            model_output=np.array([[0.0] * 5]),  # shape de distancias esperada (1, n_neighbors)
        )

        mlflow.sklearn.log_model(
            model,
            artifact_path="model_engine",
            input_example=X_example,
            signature=signature,
        )

        # 2. Bundle completo para la API:
        #    - model        → NearestNeighbors ya entrenado
        #    - vectorizer   → TfidfVectorizer ya ajustado
        #    - scaler       → MinMaxScaler ya ajustado
        #    - input_schema → dict con los campos y tipos esperados por la API
        #    - transform_fn → referencia a la función de preprocesamiento
        artifacts_bundle = {
            "model": model,
            "vectorizer": tfidf,
            "scaler": scaler,
            "input_schema": {
                "breed": "str  — raza del caballo (e.g. 'Thoroughbred')",
                "color": "str  — color del pelaje (e.g. 'bay')",
                "price": "float — precio de referencia en USD",
            },
            "transform_fn": transform_input,   # función importada, no lambda
        }

        # Bundle → MLflow (delete=False por compatibilidad Windows)
        tmp = tempfile.NamedTemporaryFile(suffix=".joblib", delete=False)
        try:
            tmp.close()  # cerrar antes de escribir (necesario en Windows)
            joblib.dump(artifacts_bundle, tmp.name)
            mlflow.log_artifact(tmp.name, artifact_path="artifacts_bundle")
        finally:
            Path(tmp.name).unlink(missing_ok=True)  # borrar siempre, incluso si falla

        # 3. Input example como CSV en memoria → MLflow
        csv_buffer = io.StringIO()
        input_example.to_csv(csv_buffer, index=False)
        mlflow.log_text(csv_buffer.getvalue(), artifact_file="artifacts_bundle/input_example.csv")

        mlflow.set_tag("status", "champion")  # marcar este modelo como el mejor hasta ahora


if __name__ == "__main__":
    main()