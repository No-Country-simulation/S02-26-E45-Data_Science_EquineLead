# genera_dataset_prueba.py
import pandas as pd
import numpy as np
from pathlib import Path

# Ruta donde guardar
PATH_DATA = Path("./data/clean")
PATH_DATA.mkdir(parents=True, exist_ok=True)

# Número de filas
N = 1000

# Generamos un dataset sintético
df = pd.DataFrame({
    "feature_1": np.random.normal(0, 1, N),
    "feature_2": np.random.normal(5, 2, N),
    "feature_3": np.random.randint(0, 10, N),
    "target": np.random.normal(10, 3, N)
})

# Guardamos en parquet
df.to_parquet(PATH_DATA / "dataset_name.parquet", index=False)

print("Dataset de prueba generado:", PATH_DATA / "dataset_name.parquet")
