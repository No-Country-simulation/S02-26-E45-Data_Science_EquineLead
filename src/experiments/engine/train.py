import sys
from pathlib import Path
import platform
import datetime
import mlflow
import pandas as pd
from sklearn.neighbors import NearestNeighbors


sys.path.append(str(Path(__file__).resolve().parents[2]))

from misc.config import init_mlflow, start_run, SEED, MLFLOW_EXPERIMENT_ENGINE_NAME
from misc.utils import log_dataset_metadata
from metrics import evaluate  # Usaremos tu función de evaluación

# =================================================================
# CONFIGURACIÓN DE RUTA ABSOLUTA (Ruta Daisy)
# =================================================================
RUTA_ABS_ARCHIVO = Path("./data/clean/horses_listings_limpio.parquet")
DATASET_NAME = "horses_listings_limpio.parquet"

RUN_NAME = f"knn_cosine_recommender_{datetime.datetime.now():%Y%m%d_%H%M%S}"
DS_NAME = "Daisy Quinteros Silva"
STAGE = "training"


def main():

    init_mlflow(experiment_name=MLFLOW_EXPERIMENT_ENGINE_NAME)

    with start_run(run_name=RUN_NAME, ds_name=DS_NAME, stage=STAGE):
        print(f"\n🔄 CARGANDO DATOS DESDE: {RUTA_ABS_ARCHIVO}")

        # 2. CARGA DE DATOS
        if not RUTA_ABS_ARCHIVO.exists():
            print(f"❌ ERROR CRÍTICO: El archivo no está en {RUTA_ABS_ARCHIVO}")
            return

        df = pd.read_parquet(RUTA_ABS_ARCHIVO)

        # 3. PROCESAMIENTO PARA RECOMENDADOR (Selección de columna)
        # Buscamos 'price' o la primera columna numérica disponible
        if "price" in df.columns:
            df_processed = df[["price"]].dropna()
            print("✅ Usando columna 'price' para Similitud de Coseno.")
        else:
            cols_num = df.select_dtypes(include=["number"]).columns
            df_processed = df[[cols_num[0]]].dropna()
            print(f"⚠️ Columna 'price' no encontrada, usando '{cols_num[0]}'.")

        # --- MOTOR DE RECOMENDACIÓN (KNN con Similitud de Coseno) ---

        model_knn = NearestNeighbors(metric="cosine", algorithm="brute")
        model_knn.fit(df_processed)
        print("🚀 Motor KNN entrenado con métrica de Coseno.")

        # 4. EVALUACIÓN (Distancias entre caballos)
        distancias, _ = model_knn.kneighbors(df_processed)

        avg_distance = distancias.mean()
        mlflow.log_metric("avg_cosine_distance", avg_distance)
        print(f"📊 Distancia media de similitud: {avg_distance}")

        # 5. REGISTRO DE METADATOS Y PARÁMETROS
        log_dataset_metadata(
            name="horses_listings",
            version="v1.0.1",
            path=f"/clean/{DATASET_NAME}",
            n_rows=df.shape[0],
            n_cols=df.shape[1],
        )

        mlflow.log_param("model_type", "NearestNeighbors")
        mlflow.log_param("metric", "cosine")
        mlflow.log_param("python_version", sys.version)
        mlflow.log_param("os", platform.system())

        # 6. GUARDAR EL MODELO EN DAGSHUB
        mlflow.sklearn.log_model(model_knn, artifact_path="model_engine")

        print(f"\n✅ ¡ÉXITO TOTAL! Experimento de RECOMENDACIÓN registrado: {RUN_NAME}")


if __name__ == "__main__":
    main()
