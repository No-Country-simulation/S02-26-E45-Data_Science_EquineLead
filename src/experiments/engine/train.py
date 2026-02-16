import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from experiments.misc.config import init_mlflow, start_run, SEED, MLFLOW_EXPERIMENT_ENGINE_NAME
from experiments.misc.utils import load_dataset, log_dataset_metadata
import mlflow
from features import build_features
from model import train_model
from metrics import evaluate
import platform
import datetime

PATH_DATA = Path("./data/clean")
DATASET_NAME = "dataset_name.parquet"

# ==================================
# DATA SCIENTIST PERSONAL CONFIG
# ==================================
RUN_NAME=f"baseline_xgboost_v1_{datetime.datetime.now():%Y%m%d_%H%M%S}"   # Ejecución puntual dentro de un experimento
DS_NAME="Pepito_Pepin"
STAGE="training"

# Registro de modelos en MLflow – Guía para Data Scientists
#
# Elegí el método de logeo según el framework con el que fue entrenado el modelo.
# Usar el logger correcto garantiza:
#   - Reproducibilidad
#   - Serialización correcta
#   - Compatibilidad con MLflow Model Registry y despliegues
#
# USAR mlflow.sklearn.log_model(model, artifact_path) SI:
#   - El modelo es de scikit-learn:
#       * LinearRegression, LogisticRegression
#       * RandomForest, GradientBoosting
#       * SVM, KNN, Naive Bayes
#   - El modelo usa una API compatible con sklearn:
#       * XGBoost (XGBClassifier / XGBRegressor)
#       * LightGBM (LGBMClassifier / LGBMRegressor)
#       * CatBoost (CatBoostClassifier / CatBoostRegressor)
#
# USAR el logger ESPECÍFICO del framework cuando esté disponible:
#   - Modelos PyTorch            → mlflow.pytorch.log_model
#   - Modelos TensorFlow / Keras → mlflow.tensorflow.log_model
#   - XGBoost nativo (Booster)   → mlflow.xgboost.log_model
#   - LightGBM nativo            → mlflow.lightgbm.log_model
#   - Statsmodels                → mlflow.statsmodels.log_model
#   - Spark MLlib                → mlflow.spark.log_model
#
# USAR mlflow.pyfunc.log_model SI:
#   - El modelo es custom o no pertenece a un framework conocido
#   - El modelo es heurístico, basado en reglas o lógica propia
#   - No estás seguro de la compatibilidad con MLflow
#
# IMPORTANTE:
#   - NO usar mlflow.sklearn.log_model para deep learning
#   - Preferir siempre el logger específico del framework antes que pyfunc
#   - En caso de duda, usar mlflow.pyfunc.log_model como fallback
#
# Esta convención es obligatoria para mantener un registry limpio y deployable.

def main():
    init_mlflow(experiment_name=MLFLOW_EXPERIMENT_ENGINE_NAME)

    with start_run(
        run_name=RUN_NAME,
        ds_name=DS_NAME,
        stage=STAGE
    ):
        # =====================
        # Load dataset
        # =====================
        df = load_dataset(path=PATH_DATA / DATASET_NAME)

        # =====================
        # Feature Engineering
        # =====================
        X_train, X_val, y_train, y_val = build_features(df=df, random_state=SEED)

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
            version="v1.0.1",
            path="/clean/horses_listings_limpio.parquet",
            n_rows=df.shape[0],
            n_cols=df.shape[1],
        )

        # =====================
        # Reproducibility
        # =====================
        mlflow.log_param("random_state", SEED)
        mlflow.log_param("cv_folds", 5)

        # =====================
        # Environment
        # =====================
        mlflow.log_param("python_version", sys.version)
        mlflow.log_param("os", platform.system())

        # =====================
        # Model Info
        # =====================
        mlflow.log_param("model_type", model.__class__.__name__)
        mlflow.log_param("model_family", "tree-based")

        # =====================
        # Artifacts
        # =====================
        mlflow.sklearn.log_model(
            model,
            artifact_path="model_leads_horses"
        )


if __name__ == "__main__":
    main()