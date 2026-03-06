from typing import Dict

from scipy.sparse import csr_matrix


def evaluate(model, X_val: csr_matrix, y_val=None) -> Dict[str, float]:
    """
    Evaluate KNN recommender reliability.
    Excludes first neighbor (self-match) when evaluating on training data.
    """

    distancias, _ = model.kneighbors(X_val)

    # Exclude self-match at index 0
    avg_distance = distancias[:, 1:].mean()
    reliability = (1 - avg_distance) * 100

    return {
        "avg_cosine_distance": avg_distance,
        "model_reliability_score": reliability,
    }
