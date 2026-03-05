from typing import Any
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors


def train_model(X_train: csr_matrix, y_train=None, random_state: int = 42) -> Any:
    """
    Train and return a KNN model with cosine similarity over sparse feature matrix.
    y_train is unused (unsupervised), kept for API consistency.
    """

    model = NearestNeighbors(n_neighbors=5, metric="cosine", algorithm="brute")
    model.fit(X_train)

    return model
