from typing import Tuple
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np

def build_features(
    df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Load data, build features and return train/validation split.
    """

    ## Ejemplo ####################################
    X = df.drop(columns=["target"])
    y = df["target"]

    X["feature_1_squared"] = X["feature_1"] ** 2
    X["feature_2_log"] = np.log1p(X["feature_2"])

    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state
    )
    ##############################################

    return X_train, X_val, y_train, y_val