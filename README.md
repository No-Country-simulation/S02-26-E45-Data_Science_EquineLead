# 📦 Subida de datos a Google Cloud Storage (GCS)

Este repositorio explica **cómo subir datos al bucket compartido de GCS** usando **Python**, pensado para usuarios que **nunca usaron Google Cloud**.

El bucket de destino es:

```
gs://equinelead-datalake
```

No se usan claves ni credenciales manuales: **todo funciona con login de Google**.

---

## 🧠 Qué vas a poder hacer

- Autenticarte en Google Cloud
- Ver el bucket compartido
- Subir archivos o carpetas completas a GCS
- Trabajar con Python usando **uv**

---

## 1️⃣ Requisitos

- Cuenta Google (la misma que está en el Google Group)
- Python 3.9 o superior
- Conexión a internet

---

## 2️⃣ Instalar Google Cloud CLI

Descargá el instalador desde:

```
https://cloud.google.com/sdk/docs/install
```

Durante la instalación:
- Aceptá todas las opciones por defecto

Verificá la instalación:

```bash
gcloud --version
```

---

## 3️⃣ Iniciar sesión en Google Cloud

En una terminal:

```bash
gcloud auth login
```

- Se abrirá el navegador
- Iniciá sesión con tu cuenta Google
- Usá **la cuenta que pertenece al Google Group**

Verificar sesión activa:

```bash
gcloud auth list
```

---

## 4️⃣ Verificar acceso al bucket

```bash
gcloud storage ls gs://equinelead-datalake
```

Si ves archivos o carpetas → el acceso está OK ✅

---

## 5️⃣ Preparar entorno Python con UV

Este proyecto usa **uv** para manejar dependencias y entorno virtual.

### Instalar uv

#### Windows (PowerShell)
```powershell
pip install uv
```

#### Linux / Mac
```bash
pip install uv
```

Verificar instalación:
```bash
uv --version
```

---

### Sincronizar entorno del proyecto

Desde la raíz del proyecto (donde está `pyproject.toml`):

```bash
uv sync --dev
```

Esto:
- Crea el entorno virtual automáticamente
- Instala todas las dependencias necesarias

No hace falta crear ni activar `.venv` manualmente.

---

### Ejecutar comandos con uv

```bash
uv run python script.py
```

---

## 6️⃣ Función para subir datos a GCS

Crear un archivo `upload_to_gcs.py` con el siguiente contenido:

```python
from google.cloud import storage
from pathlib import Path

def upload_to_clean_bucket(
    local_path: str,
    bucket_name: str = "equinelead-datalake",
    clean_prefix: str = "clean"
):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    local_path = Path(local_path)

    if local_path.is_file():
        blob_path = f"{clean_prefix}/{local_path.name}"
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(local_path)
        print(f"Subido: gs://{bucket_name}/{blob_path}")

    elif local_path.is_dir():
        for file in local_path.rglob("*"):
            if file.is_file():
                relative_path = file.relative_to(local_path)
                blob_path = f"{clean_prefix}/{relative_path}"
                blob = bucket.blob(str(blob_path))
                blob.upload_from_filename(file)
                print(f"Subido: gs://{bucket_name}/{blob_path}")
```

---

## 7️⃣ Uso

### Subir un archivo

```python
from upload_to_gcs import upload_to_clean_bucket
upload_to_clean_bucket("data/clean/horses_clean.parquet")
```

### Subir una carpeta completa

```python
from upload_to_gcs import upload_to_clean_bucket
upload_to_clean_bucket("data/clean/")
```

Los archivos quedarán en:

```
gs://equinelead-datalake/clean/
```

---

## ❌ Errores comunes

### 403 Forbidden
No tenés permisos para subir archivos.  
Contactar al administrador del bucket.

### El bucket no aparece
- Estás usando otra cuenta Google
- No tenés permisos de visualización

Verificar cuenta activa:

```bash
gcloud auth list
```
---

## ✅ Listo

Con esto ya podés trabajar con el datalake compartido de forma segura y simple.
