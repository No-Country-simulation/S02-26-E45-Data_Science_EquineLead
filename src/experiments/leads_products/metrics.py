from typing import Dict
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error


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
        "rmse": mean_squared_error(y_val, preds, squared=False),
        "mae": mean_absolute_error(y_val, preds),
    }
