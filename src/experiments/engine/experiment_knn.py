import pandas as pd
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import hstack

def run_experiment():
    print("🚀 Iniciando Experimento: Motor de Recomendación Equina")
    
    # 1. Carga de datos (Ajustado con 3 saltos para llegar a la raíz del repo)
    try:
        df_horses = pd.read_parquet('../../../horses_listings_limpio.parquet')
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo .parquet en la raíz. Revisa la ruta.")
        return
    
    # 2. Preprocesamiento Técnico
    df_horses.columns = [c.lower().strip() for c in df_horses.columns]
    df_horses['price'] = pd.to_numeric(df_horses['price'], errors='coerce').fillna(0)
    df_horses = df_horses.dropna(subset=['name'])
    
    # 3. Feature Engineering (TF-IDF + Scaling)
    tfidf = TfidfVectorizer(max_features=100)
    df_horses['caracteristicas'] = (
        df_horses['breed'].fillna('') + " " + 
        df_horses['color'].fillna('')
    ).str.lower()
    matrix_features = tfidf.fit_transform(df_horses['caracteristicas'])
    
    scaler = MinMaxScaler()
    price_scaled = scaler.fit_transform(df_horses[['price']])
    
    # 4. Construcción de Matriz CSR (Optimización de Memoria)
    X_combined = hstack([matrix_features, price_scaled]).tocsr()
    
    # 5. Entrenamiento del Modelo
    model_pro = NearestNeighbors(n_neighbors=5, metric='cosine', algorithm='brute')
    model_pro.fit(X_combined)
    
    # 6. Cálculo de Métrica de Fiabilidad
    distancias, _ = model_pro.kneighbors(X_combined)
    similitudes = (1 - distancias[:, 1:]) * 100
    avg_reliability = np.mean(similitudes)
    
    print(f"📊 Resultado del Experimento: {avg_reliability:.2f}% de fiabilidad")
    
    # 7. Exportación de Artefactos (Diccionario para Producción)
    artifacts = {
        "model": model_pro,
        "vectorizer": tfidf,
        "scaler": scaler,
        "matrix": X_combined
    }
    
    joblib.dump(artifacts, 'recommendation_artifacts_v1.joblib')
    print("✅ Artefactos registrados en 'recommendation_artifacts_v1.joblib'")

if __name__ == "__main__":
    run_experiment()