import mlflow
import dagshub


# =========================
# DagsHub / MLflow Setup
# =========================

DAGSHUB_REPO_OWNER = "aletbm"
DAGSHUB_REPO_NAME = "S02-26-E45-Data_Science_EquineLead"
MLFLOW_EXPERIMENT_HORSES_NAME = "equinelead-leads-horses"
MLFLOW_EXPERIMENT_PRODUCTS_NAME = "equinelead-leads-horses"
SEED = 42

def init_mlflow(experiment_name: str):
    """
    Initialize MLflow tracking with DagsHub backend.
    Safe to call multiple times.
    """

    dagshub.init(
        repo_owner=DAGSHUB_REPO_OWNER,
        repo_name=DAGSHUB_REPO_NAME,
        mlflow=True
    )

    mlflow.set_experiment(experiment_name)


# =========================
# Helpers
# =========================

def start_run(
    run_name: str | None = None,
    ds_name: str | None = None,
    stage: str = "dev",
    tags: dict | None = None,
):
    """
    Wrapper around mlflow.start_run with standard tags.
    """

    default_tags = {
        "team": "equinelead",
        "stage": stage,
    }

    if ds_name:
        default_tags["ds_name"] = ds_name

    if tags:
        default_tags.update(tags)

    return mlflow.start_run(
        run_name=run_name,
        tags=default_tags
    )
