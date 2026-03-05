import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from misc.config import init_mlflow, start_run, SEED, MLFLOW_EXPERIMENT_ENGINE_NAME
from misc.utils import load_dataset, log_dataset_metadata
import mlflow
import joblib
from features import build_features
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
        # Artifacts
        # =====================
        mlflow.sklearn.log_model(
            model,
            artifact_path="model_engine",
            registered_model_name="model_engine",
        )

        # Export artifacts bundle for API consumption
        joblib.dump(
            {"model": model, "vectorizer": tfidf, "scaler": scaler},
            "recommendation_artifacts_v1.joblib",
        )


if __name__ == "__main__":
    main()