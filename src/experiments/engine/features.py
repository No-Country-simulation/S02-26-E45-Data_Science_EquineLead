from typing import Tuple
import pandas as pd
import numpy as np

def build_features(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Load data, build features and return the processed dataframe for recommendation.
    """

    ## Implementación Motor de Recomendación ########################
    # Limpieza de nombres de columnas
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Creación de columna combinada para el Vectorizador/Modelo
    df['combined_features'] = (
        df['breed'].fillna('') + " " + 
        df['color'].fillna('') + " " + 
        df['gender'].fillna('')
    ).str.lower()
    
    # Aseguramos que el precio sea numérico para el modelo
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
    ##############################################################

    return df