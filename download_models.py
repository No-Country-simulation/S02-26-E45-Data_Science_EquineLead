import os
import dagshub
import mlflow
from mlflow.tracking import MlflowClient

os.environ["MLFLOW_TRACKING_URI"] = "https://dagshub.com/aletbm/S02-26-E45-Data_Science_EquineLead.mlflow"

def download_models():
    client = MlflowClient()
    experiments = client.search_experiments()
    os.makedirs("models_downloaded", exist_ok=True)
    count = 0
    for exp in experiments:
        exp_name = exp.name
        if exp_name == "Default":
            continue
        runs = client.search_runs(
            experiment_ids=[exp.experiment_id],
            order_by=["attribute.start_time DESC"],
            max_results=5
        )
        if not runs:
            continue
        for run in runs:
            run_id = run.info.run_id
            print(f"Checking artifacts for run {run_id} ({exp_name})")
            artifacts = client.list_artifacts(run_id)
            if not artifacts:
                continue
            
            for art in artifacts:
                print(f"Downloading artifact {art.path}")
                try:
                    local_path = mlflow.artifacts.download_artifacts(
                        run_id=run_id, 
                        artifact_path=art.path, 
                        dst_path=f"models_downloaded/{exp_name}_{run_id}"
                    )
                    print(f"Downloaded to {local_path}")
                    count += 1
                except Exception as e:
                    print(f"Failed to download {art.path}: {e}")
            # If we downloaded anything for this run, we can stop and go to next experiment or just get all
            if count > 0:
                break
                
    if count == 0:
        print("Could not download any models.")

if __name__ == "__main__":
    download_models()
