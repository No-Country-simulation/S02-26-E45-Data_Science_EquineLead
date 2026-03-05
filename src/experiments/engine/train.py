import sys
from pathlib import Path
import datetime
import mlflow
import pandas as pd
import joblib
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import hstack

# Configuración de rutas
sys.path.append(str(Path(__file__).resolve().parents[2]))

from misc.config import init_mlflow, start_run, MLFLOW_EXPERIMENT_ENGINE_NAME
from misc.utils import log_dataset_metadata

# =================================================================
# CONFIGURACIÓN DE RUTA ABSOLUTA
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

        if not RUTA_ABS_ARCHIVO.exists():
            print(f"❌ ERROR CRÍTICO: El archivo no está en {RUTA_ABS_ARCHIVO}")
            return

        df = pd.read_parquet(RUTA_ABS_ARCHIVO)
        df.columns = [c.lower().strip() for c in df.columns]

        # =================================================================
        # 3. FEATURE ENGINEERING MULTIDIMENSIONAL (Tu lógica de experimento)
        # =================================================================
        print("🛠️ Iniciando Feature Engineering...")

        # Procesamiento de Texto (Raza + Color)
        tfidf = TfidfVectorizer(max_features=100)
        df["caracteristicas"] = (
            df["breed"].fillna("desconocido") + " " + df["color"].fillna("desconocido")
        ).str.lower()
        matrix_text = tfidf.fit_transform(df["caracteristicas"])

        # Procesamiento de Precio
        scaler = MinMaxScaler()
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
        price_scaled = scaler.fit_transform(df[["price"]])

        # Unión de características en matriz CSR (Optimización)
        X_combined = hstack([matrix_text, price_scaled]).tocsr()
        print(
            f"✅ Matriz creada: {X_combined.shape[0]} registros y {X_combined.shape[1]} dimensiones."
        )

        # =================================================================
        # 4. ENTRENAMIENTO DEL MOTOR
        # =================================================================
        model_knn = NearestNeighbors(n_neighbors=5, metric="cosine", algorithm="brute")
        model_knn.fit(X_combined)
        print("🚀 Motor KNN entrenado con Similitud de Coseno.")

        # =================================================================
        # 5. EVALUACIÓN Y MÉTRICAS (MLflow)
        # =================================================================
        distancias, _ = model_knn.kneighbors(X_combined)

        # Calculamos la fiabilidad basada en la distancia (1 - distancia = similitud)
        # Tomamos del segundo vecino en adelante porque el primero es el mismo caballo (distancia 0)
        avg_distance = distancias[:, 1:].mean()
        reliability = (1 - avg_distance) * 100

        mlflow.log_metric("avg_cosine_distance", avg_distance)
        mlflow.log_metric("model_reliability_score", reliability)

        print(f"📊 Distancia media: {avg_distance:.4f}")
        print(f"📊 Fiabilidad del modelo: {reliability:.2f}%")

        # =================================================================
        # 6. REGISTRO DE PARÁMETROS Y ARTEFACTOS
        # =================================================================
        log_dataset_metadata(
            name="horses_listings",
            version="v1.0.2",
            path=f"/clean/{DATASET_NAME}",
            n_rows=df.shape[0],
            n_cols=df.shape[1],
        )

        mlflow.log_param("features_used", "price, breed, color")
        mlflow.log_param("vectorizer_type", "TfidfVectorizer")
        mlflow.log_param("scaler_type", "MinMaxScaler")
        mlflow.log_param("model_type", "NearestNeighbors")

        # Guardar el modelo oficial en DagsHub/MLflow
        mlflow.sklearn.log_model(model_knn, artifact_path="model_engine")

        # También guardamos el diccionario de artefactos para Alex (API)
        artifacts = {"model": model_knn, "vectorizer": tfidf, "scaler": scaler}
        joblib.dump(artifacts, "recommendation_artifacts_v1.joblib")

        print("\n✅ ¡ÉXITO! Experimento registrado correctamente en DagsHub.")


if __name__ == "__main__":
    main()
