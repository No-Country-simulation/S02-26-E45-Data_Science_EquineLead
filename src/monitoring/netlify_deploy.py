import hashlib
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

NETLIFY_TOKEN = os.getenv("NETLIFY_TOKEN", "")
NETLIFY_SITE_ID = os.getenv("NETLIFY_SITE_ID", "")
NETLIFY_API = "https://api.netlify.com/api/v1"


def _sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def deploy_report(report_path: str) -> str:
    if not NETLIFY_TOKEN:
        raise ValueError("NETLIFY_TOKEN no configurado en .env")
    if not NETLIFY_SITE_ID:
        raise ValueError("NETLIFY_SITE_ID no configurado en .env")

    path = Path(report_path)
    content = path.read_bytes()
    digest = _sha1(content)
    headers = {"Authorization": f"Bearer {NETLIFY_TOKEN}"}

    # 1. Obtener dominio del site
    site_resp = requests.get(
        f"{NETLIFY_API}/sites/{NETLIFY_SITE_ID}",
        headers=headers,
    )
    site_resp.raise_for_status()
    domain = site_resp.json()["default_domain"]

    # 2. Crear deploy indicando qué archivos vamos a subir
    deploy_resp = requests.post(
        f"{NETLIFY_API}/sites/{NETLIFY_SITE_ID}/deploys",
        headers={**headers, "Content-Type": "application/json"},
        json={"files": {"/index.html": digest}},
    )
    deploy_resp.raise_for_status()
    deploy = deploy_resp.json()
    deploy_id = deploy["id"]

    # 3. Subir los archivos requeridos (Netlify sólo pide los que no tiene en caché)
    required = deploy.get("required", [])
    if digest in required:
        upload_resp = requests.put(
            f"{NETLIFY_API}/deploys/{deploy_id}/files/index.html",
            headers={
                **headers,
                "Content-Type": "text/html; charset=utf-8",
            },
            data=content,
        )
        upload_resp.raise_for_status()

    # 4. Publicar el deploy
    publish_resp = requests.post(
        f"{NETLIFY_API}/deploys/{deploy_id}/restore",
        headers=headers,
    )
    # restore puede devolver 200 o 201; ignoramos errores menores
    if publish_resp.status_code not in (200, 201):
        publish_resp.raise_for_status()

    url = f"https://{domain}/"
    print(f"✅ Reporte publicado: {url}")
    return url
