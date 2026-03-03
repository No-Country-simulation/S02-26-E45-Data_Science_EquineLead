import numpy as np
from typing import Dict

def evaluate(
    distances: np.ndarray
) -> Dict[str, float]:
    """
    Evaluate the model and return a dictionary of metrics.
    """

    ## Implementación Motor de Recomendación ########################
    # Convertimos las distancias en porcentaje de similitud (fiabilidad)
    similitudes = (1 - distances[:, 1:]) * 100
    reliability = np.mean(similitudes)
    
    metrics = {
        "reliability": reliability
    }
    ##############################################################

    return metrics