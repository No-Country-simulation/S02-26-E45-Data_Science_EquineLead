import sys
from pathlib import Path
import platform
import datetime
import mlflow
import joblib

sys.path.append(str(Path(__file__).resolve().parents[2]))

from misc.config import init_mlflow, start_run, SEED, MLFLOW_EXPERIMENT_ENGINE_NAME
from misc.utils import load_dataset, log_dataset_metadata
from features import build_features
from model import train_model
from metrics import evaluate

PATH_DATA = Path("./data/clean")
DATASET_NAME = "horses_listings_limpio.parquet" 

RUN_NAME = f"knn_horse_recommender_{datetime.datetime.now():%Y%m%d_%H%M%S}"
DS_NAME = "Daisy_Quinteros" 
STAGE = "training"

def main():
    init_mlflow(experiment_name=MLFLOW_EXPERIMENT_ENGINE_NAME)

    with start_run(
        run_name=RUN_NAME,
        ds_name=DS_NAME,
        stage=STAGE
    ):
        df = load_dataset(path=PATH_DATA / DATASET_NAME)

        df_processed = build_features(df=df)

        model = train_model(df_processed[['price']], random_state=SEED)

        distancias, _ = model.kneighbors(df_processed[['price']])
        metrics = evaluate(distancias) 

        for k, v in metrics.items():
            mlflow.log_metric(k, v)

        log_dataset_metadata(
            name="horses_listings",
            version="v1.0.1",
            path=f"/clean/{DATASET_NAME}",
            n_rows=df.shape[0],
            n_cols=df.shape[1],
        )

        mlflow.log_param("random_state", SEED)
        mlflow.log_param("python_version", sys.version)
        mlflow.log_param("os", platform.system())

        mlflow.log_param("model_type", model.__class__.__name__)
        mlflow.log_param("model_family", "Instance-based (KNN)")

        mlflow.sklearn.log_model(
            model,
            artifact_path="model_engine"
        )
        
        print(f"✅ Experimento '{RUN_NAME}' registrado en MLflow")

if __name__ == "__main__":
    main()