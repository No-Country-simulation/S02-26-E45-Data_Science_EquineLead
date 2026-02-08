from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
import subprocess
import os
import time
import json
from pathlib import Path
from prefect.client import get_client

DATA_DIR_RAW = Path("/app/data/raw")
DATA_DIR_CLEAN = Path("/app/data/clean")

GCS_BUCKET_NAME = "equinelead-datalake"
GCS_BLOCK_NAME = "equinelead-datalake"

# ---------------- TASKS ---------------- #

@task
def run_scraper(script_name: str):
    result = subprocess.run(
        ["python", script_name],
        capture_output=True,
        text=True
    )
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"Scraper failed: {script_name}")


def get_gcs_bucket():
    """Carga el bloque GCS, o lo crea si no existe"""
    try:
        bucket = GcsBucket.load(GCS_BLOCK_NAME)
        print("GcsBucket cargado ✅")
    except ValueError:
        print("GcsBucket no encontrado, creando uno nuevo...")
        with open("/secrets/gcp-key.json") as f:
            gcp_creds_dict = json.load(f)
        bucket = GcsBucket(bucket=GCS_BUCKET_NAME, gcp_credentials=gcp_creds_dict)
        bucket.save(GCS_BLOCK_NAME, overwrite=True)
        print("GcsBucket creado y guardado ✅")
    return bucket

@task
def upload_to_gcs(local_path: Path, folder: str):
    bucket = get_gcs_bucket()
    filename = local_path.name
    remote_path = f"{folder}/{filename}"
    bucket.upload_from_path(from_path=str(local_path), to_path=remote_path)
    print(f"Archivo subido a {remote_path} ✅")

@task
def debug_gcs():
    from google.cloud import storage
    client = storage.Client()
    buckets = list(client.list_buckets())
    print("Buckets visibles:", [b.name for b in buckets])

# ---------------- FLOW ---------------- #

@flow(name="equinelead_pipeline")
def equinelead_pipeline():

    # ---------- RETRY PREFECT SERVER ----------
    client = get_client()
    for i in range(20):  # hasta 20 reintentos (~60s)
        try:
            client.api_healthcheck()
            print("Prefect Server listo ✅")
            break
        except Exception:
            print("Esperando a Prefect Server...")
            time.sleep(3)
    else:
        raise RuntimeError("Prefect Server no respondió después de 60s")

    # ---------- FLOW LOGIC ----------
    mode = os.getenv("PIPELINE_MODE", "ingestion")
    debug = os.getenv("DEBUG_GCS", "False")

    if debug != "False":
        debug_gcs()

    if mode == "ingestion":
        # RUN SCRAPERS IN PARALLEL
        equinenow = run_scraper.submit("./scraping/equinenow_scraping.py")
        horsedeals = run_scraper.submit("./scraping/horsedeals_scraping.py")
        dovers = run_scraper.submit("./scraping/doversaddlery_scraping.py")

        # WAIT
        equinenow.result()
        horsedeals.result()
        dovers.result()

        # UPLOAD RAW DATA
        upload_to_gcs(DATA_DIR_RAW / "equinenow_horses_listings.parquet", folder="raw")
        upload_to_gcs(DATA_DIR_RAW / "horsedeals_horses_listings.parquet", folder="raw")
        upload_to_gcs(DATA_DIR_RAW / "doversaddlery_products_listing.parquet", folder="raw")

    elif mode == "clean_upload":
        upload_to_gcs(DATA_DIR_CLEAN / "equinenow_horses_listings_cl.parquet", folder="clean")
        upload_to_gcs(DATA_DIR_CLEAN / "horsedeals_horses_listings_cl.parquet", folder="clean")
        upload_to_gcs(DATA_DIR_CLEAN / "doversaddlery_products_listing_cl.parquet", folder="clean")

    else:
        raise ValueError(f"Modo inválido: {mode}")


if __name__ == "__main__":
    equinelead_pipeline()

# prefect cloud login -k [API_key] 
# prefect profile inspect 
# prefect block register -m 
# prefect_gcp prefect block create gcp-credentials 
# prefect block create gcs-bucket 
# prefect work-pool create --type docker equinelead-docker-pool