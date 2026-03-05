from typing import Tuple
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import hstack, csr_matrix


def build_features(
    df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42
) -> Tuple[csr_matrix, csr_matrix, pd.Series, pd.Series, TfidfVectorizer, MinMaxScaler]:
    """
    Build feature matrix combining TF-IDF (breed + color) and scaled price.
    Returns train/val sparse matrices, price target, and fitted transformers.
    """

    df.columns = [c.lower().strip() for c in df.columns]

    # Text features (breed + color)
    tfidf = TfidfVectorizer(max_features=100)
    df["caracteristicas"] = (
        df["breed"].fillna("desconocido") + " " + df["color"].fillna("desconocido")
    ).str.lower()
    matrix_text = tfidf.fit_transform(df["caracteristicas"])

    # Numeric features
    scaler = MinMaxScaler()
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
    price_scaled = scaler.fit_transform(df[["price"]])

    # Combine into sparse matrix
    X = hstack([matrix_text, price_scaled]).tocsr()
    y = df["price"]

    # Manual split preserving sparse format
    split_idx = int(len(df) * (1 - test_size))
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]

    return X_train, X_val, y_train, y_val, tfidf, scaler


def transform_input(
    data: dict | pd.DataFrame,
    tfidf: TfidfVectorizer,
    scaler: MinMaxScaler,
) -> csr_matrix:
    """
    Replicate feature engineering for API inference.

    Accepts a single dict or a DataFrame with keys/columns:
        - breed  (str)
        - color  (str)
        - price  (float | int)

    Returns a sparse CSR matrix ready for model.kneighbors().

    Example (API usage):
        input_data = {"breed": "Thoroughbred", "color": "bay", "price": 5000}
        X = transform_input(input_data, artifacts["vectorizer"], artifacts["scaler"])
        distances, indices = artifacts["model"].kneighbors(X)
    """
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        df = data.copy()

    df.columns = [c.lower().strip() for c in df.columns]

    # Text features — same logic as training
    df["caracteristicas"] = (
        df["breed"].fillna("desconocido") + " " + df["color"].fillna("desconocido")
    ).str.lower()
    matrix_text = tfidf.transform(df["caracteristicas"])  # transform, NOT fit_transform

    # Numeric features — same logic as training
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
    price_scaled = scaler.transform(df[["price"]])  # transform, NOT fit_transform

    return hstack([matrix_text, price_scaled]).tocsr()
