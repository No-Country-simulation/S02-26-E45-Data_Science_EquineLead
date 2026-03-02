from typing import Any
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    random_state: int = 42
) -> Any:
    """
    Train and return a model.
    """
    ## Ejemplo ####################################
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        random_state=random_state,
        n_jobs=-1
    )

    model.fit(X_train, y_train)
    ##############################################
    return model
