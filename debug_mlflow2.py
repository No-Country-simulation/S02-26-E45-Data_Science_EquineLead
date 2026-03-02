import os
import mlflow
from mlflow.tracking import MlflowClient

os.environ["MLFLOW_TRACKING_URI"] = "https://dagshub.com/aletbm/S02-26-E45-Data_Science_EquineLead.mlflow"
mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
client = MlflowClient()

experiments = client.search_experiments()
for exp in experiments:
    if exp.name == "Default": continue
    print(f"\\n--- Experiment: {exp.name} (ID: {exp.experiment_id}) ---")
    
    # Try getting all runs without order_by constraint first to see if that's the issue
    try:
        runs = client.search_runs(experiment_ids=[exp.experiment_id])
        print(f"Total Runs found: {len(runs)}")
        for r in runs[:2]:
            print(f"  Run ID: {r.info.run_id}, Name: {r.info.run_name}")
            print(f"  Metrics keys: {list(r.data.metrics.keys())}")
            print(f"  Params keys: {list(r.data.params.keys())}")
    except Exception as e:
        print(f"Error fetching runs: {e}")
