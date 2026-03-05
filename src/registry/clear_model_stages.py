import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from misc.config import init_mlflow
import mlflow

init_mlflow()

client = mlflow.tracking.MlflowClient()


def clear_stages(model_name: str):
    """Limpia el stage de todas las versiones de un modelo"""
    versions = client.search_model_versions(f"name='{model_name}'")

    for v in versions:
        if v.current_stage != "None":
            client.transition_model_version_stage(
                name=model_name,
                version=v.version,
                stage="None",  # quita el stage completamente
            )
            print(
                f"✅ {model_name} v{v.version} → stage removido (era: {v.current_stage})"
            )
        else:
            print(f"   {model_name} v{v.version} → ya estaba sin stage")


if __name__ == "__main__":
    # Limpiar un modelo específico
    clear_stages("HORSE_P1")
    clear_stages("HORSE_P2")
    clear_stages("PRODS_P1")
    clear_stages("PRODS_P2")
