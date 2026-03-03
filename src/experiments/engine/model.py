from typing import Any
import pandas as pd
from sklearn.neighbors import NearestNeighbors

def train_model(
    X_train: pd.DataFrame,
    random_state: int = 42
) -> Any:
    """
    Train and return a model.
    """
    ## Implementación Motor de Recomendación ########################
    model = NearestNeighbors(
        n_neighbors=5, 
        metric='cosine', 
        algorithm='brute'
    )
    model.fit(X_train)
    ##############################################################
    return model