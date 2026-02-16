from typing import Dict
import pandas as pd
from sklearn.metrics import root_mean_squared_error, mean_absolute_error


def evaluate(
    model,
    X_val: pd.DataFrame,
    y_val: pd.Series
) -> Dict[str, float]:
    """
    Evaluate model and return metrics dict.
    """
    
    # Ejemplo ####################################
    preds = model.predict(X_val)

    return {
        "rmse": root_mean_squared_error(y_val, preds),
        "mae": mean_absolute_error(y_val, preds),
    }
