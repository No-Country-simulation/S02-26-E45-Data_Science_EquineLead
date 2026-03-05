import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from misc.config import init_mlflow
import mlflow
import pickle
import os
import datetime
import pandas as pd
from mlflow.models import infer_signature
from category_encoders import TargetEncoder

# Mapeo de dominio a experiment_id
EXPERIMENT_MAP = {
    "horse": "2",
    "prods": "1",
}

# Columnas categóricas que requieren TargetEncoder
COLS_TARGET_ENCODE = ["user_region", "user_card_issuer", "user_domain"]

# Mapeo de target para TargetEncoder
TARGET_MAP = {"Lead Bronce": 0, "Lead Plata": 1, "Lead Oro": 2}

RUN_ID = "dd6f2989958a48d587e2769933622ff8"


def get_log_model_fn(model):
    module = type(model).__module__
    if "xgboost" in module:
        return mlflow.xgboost.log_model
    elif "lightgbm" in module:
        return mlflow.lightgbm.log_model
    elif "sklearn" in module:
        return mlflow.sklearn.log_model
    elif "catboost" in module:
        return mlflow.catboost.log_model
    else:
        return mlflow.pyfunc.log_model


def get_run_id(run_id=None, experiment_name=None):
    if run_id:
        return run_id

    if experiment_name:
        exp = client.get_experiment_by_name(experiment_name)
        experiment_ids = [exp.experiment_id]
    else:
        experiment_ids = [e.experiment_id for e in client.search_experiments()]

    runs = client.search_runs(
        experiment_ids=experiment_ids,
        filter_string="tags.status = 'champion'",
        max_results=1,
    )

    if not runs:
        raise ValueError("No se encontró ningún run con tag status='champion'")

    print(f"Champion: {runs[0].info.run_name} ({runs[0].info.run_id})")
    return runs[0].info.run_id


def filter_params(params: dict, paso: str) -> dict:
    return {k: v for k, v in params.items() if k.startswith(paso)}


def filter_metrics(metrics: dict, dominio: str, paso_label: str) -> dict:
    def belongs(key):
        if not key.endswith(f"_{dominio}"):
            return False
        if "paso" in key or "overfit" in key:
            return paso_label in key
        return True

    return {k: v for k, v in metrics.items() if belongs(k)}


def download_artifact(run_id: str, file_path: str, folder_path: str) -> str:
    dst_path = f"./models/{run_id}/{folder_path}/"
    os.makedirs(dst_path, exist_ok=True)
    local_path = client.download_artifacts(run_id, file_path, dst_path=dst_path)
    print(f"\nLocal path: {local_path} ({os.path.getsize(local_path)} bytes)")
    return local_path


def load_model(local_path: str, file_path: str):
    try:
        with open(local_path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error cargando {file_path}: {e}")
        return None


def encode_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    target_ord = df["horse_target"].map(TARGET_MAP)
    te = TargetEncoder(cols=COLS_TARGET_ENCODE, smoothing=10)
    df_encoded = df.copy()
    df_encoded[COLS_TARGET_ENCODE] = te.fit_transform(
        df[COLS_TARGET_ENCODE], target_ord
    )
    return df_encoded


def find_pkl_artifacts(run_id: str):
    """Busca .pkl recursivamente tanto en artifacts sueltos como en subcarpetas"""
    found = []

    def walk(path=""):
        items = client.list_artifacts(run_id, path)
        for item in items:
            if item.is_dir:
                walk(item.path)
            elif item.path.endswith(".pkl"):
                folder_path = str(Path(item.path).parent)
                found.append((item.path, folder_path))

    walk()
    return found


def build_signature(model, df: pd.DataFrame):
    try:
        feature_names = model.feature_names_in_.tolist()
        df_encoded = encode_dataframe(df)
        input_example = df_encoded[feature_names].iloc[[0]]

        input_example = input_example.copy()
        int_cols = input_example.select_dtypes(include="integer").columns
        input_example[int_cols] = input_example[int_cols].astype("float64")

        predictions = model.predict(input_example)

        signature = infer_signature(
            model_input=input_example,
            model_output=predictions,
        )
        print(f"   ✅ Firma inferida: {len(feature_names)} features")
        return signature, input_example

    except AttributeError:
        print("⚠️  El modelo no tiene feature_names_in_, sin firma")
        return None, None


def log_model_to_registry(
    model,
    log_model_fn,
    folder_name: str,
    registered_name: str,
    experiment_id: str,
    new_run_name: str,
    params: dict,
    metrics: dict,
    alias: str,
    source_run_id: str,
    source_run_name: str,
    paso: str,
    dominio: str,
    signature,
    input_example,
):
    with mlflow.start_run(run_name=new_run_name, experiment_id=experiment_id):
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)

        log_model_fn(
            model,
            name=folder_name,
            registered_model_name=registered_name,
            signature=signature,
            input_example=input_example,
        )

        mlflow.set_tag("parent_run_id", source_run_id)
        mlflow.set_tag("parent_run_name", source_run_name)
        mlflow.set_tag("status", "champion_derived")
        mlflow.set_tag("dominio", dominio)
        mlflow.set_tag("paso", paso)


def assign_alias(registered_name: str, alias: str):
    versions = client.search_model_versions(f"name='{registered_name}'")
    latest_version = max(versions, key=lambda v: int(v.version))
    client.set_registered_model_alias(
        name=registered_name,
        alias=alias,
        version=latest_version.version,
    )
    print(
        f"✅ Registrado como: {registered_name} con alias '{alias}' → v{latest_version.version}"
    )


def handle_models(
    run_id=None,
    experiment_name=None,
    register=False,
    alias="staging",
    df=None,
):
    now = datetime.datetime.now()

    run_id = get_run_id(run_id=run_id, experiment_name=experiment_name)
    run = client.get_run(run_id)
    run_name = run.info.run_name
    print(f"Nombre del run: {run_name}")

    for file_path, folder_path in find_pkl_artifacts(run_id):
        local_path = download_artifact(run_id, file_path, folder_path)

        if not register:
            continue

        model = load_model(local_path, file_path)
        if model is None:
            continue

        # Extraer paso y dominio del nombre de la carpeta
        # ej: "modelo_p1_horse" → paso="p1", dominio="horse"
        parts = Path(folder_path).name.split("_")
        paso = parts[1]  # "p1" o "p2"
        dominio = parts[-1]  # "horse" o "prods"
        paso_label = paso.replace("p", "paso")  # "paso1" o "paso2"

        log_model_fn = get_log_model_fn(model)
        params_filtrados = filter_params(run.data.params, paso)
        metricas_filtradas = filter_metrics(run.data.metrics, dominio, paso_label)
        registered_name = f"{dominio.upper()}_{paso.upper()}"
        new_run_name = f"{run_name}_{'_'.join(parts[-2:])}_{now:%Y%m%d_%H%M%S}"

        print(f"   {folder_path} → {type(model).__name__} → {log_model_fn.__module__}")
        print(f"   Params: {list(params_filtrados.keys())}")
        print(f"   Métricas: {list(metricas_filtradas.keys())}")

        signature, input_example = (
            build_signature(model, df) if df is not None else (None, None)
        )

        log_model_to_registry(
            model=model,
            log_model_fn=log_model_fn,
            folder_name=folder_path,
            registered_name=registered_name,
            experiment_id=EXPERIMENT_MAP[dominio],
            new_run_name=new_run_name,
            params=params_filtrados,
            metrics=metricas_filtradas,
            alias=alias,
            source_run_id=run_id,
            source_run_name=run_name,
            paso=paso,
            dominio=dominio,
            signature=signature,
            input_example=input_example,
        )

        assign_alias(registered_name, alias)


init_mlflow()

client = mlflow.tracking.MlflowClient()

if __name__ == "__main__":
    df = pd.read_parquet("./data/clean/df_final.parquet")

    # Solo descargar
    # handle_models(run_id=RUN_ID)

    # Descargar y registrar con alias "staging" por defecto
    # handle_models(run_id=RUN_ID, register=True, df=df)

    # Descargar y registrar con alias custom
    handle_models(run_id=RUN_ID, register=True, alias="staging", df=df)

    # Por champion
    # handle_models(experiment_name="nombre_experimento", register=True, df=df)
    # handle_models(register=True, df=df)
