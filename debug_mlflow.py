import os
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd

os.environ['MLFLOW_TRACKING_URI'] = 'https://dagshub.com/aletbm/S02-26-E45-Data_Science_EquineLead.mlflow'
mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])

client = MlflowClient()
exps = client.search_experiments()
for exp in exps:
    if exp.name == 'EquineLead_LeadScoring':
        runs = client.search_runs([exp.experiment_id])
        if runs:
            r = runs[0]
            print("Run Name:", r.info.run_name)
            print("Run ID:", r.info.run_id)
            print("Metrics:", r.data.metrics)
            print("Params:", r.data.params)
            artifacts = client.list_artifacts(r.info.run_id)
            print("Artifacts:", [a.path for a in artifacts])
        break

try:
    df_h = pd.read_parquet('data/clean/horses_listings_limpio.parquet')
    print('Horse Price:', df_h['Price'].describe() if 'Price' in df_h else 'None')
    if 'Price' in df_h:
        print('Horse Price 99th percentile:', df_h['Price'].quantile(0.99))
    
    df_p = pd.read_parquet('data/clean/products_listing_limpio.parquet')
    print('Product Price:', df_p['Price'].describe() if 'Price' in df_p else 'None')
    if 'Price' in df_p:
        print('Product Price 99th percentile:', df_p['Price'].quantile(0.99))
except Exception as e:
    print("Error reading parquet:", e)
