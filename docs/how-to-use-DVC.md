# Guía: Descargar datos con DVC — Equipo EquineLead

## Requisitos previos

- Tener acceso al repositorio en **DagsHub**
- Tener acceso al bucket **GCS** (`equinelead-datalake`)
- Tener instalado **Python >= 3.11**
- Tener instalado **gcloud CLI** → [Descargar aquí](https://cloud.google.com/sdk/docs/install)

---

## 1. Clonar el repositorio

```bash
git clone https://github.com/No-Country-simulation/S02-26-E45-Data_Science_EquineLead.git
cd S02-26-E45-Data_Science_EquineLead
```

---

## 2. Instalar dependencias

```bash

uv sync

```

---

## 3. Autenticarse en Google Cloud con tus propias credenciales

> ⚠️ Cada integrante debe autenticarse con **su propia cuenta de Google** que tenga acceso al bucket.

```bash
# Login interactivo (abre el navegador)
gcloud auth application-default login

# Verificar que estás autenticado correctamente
gcloud auth list

# Setear el proyecto correcto
gcloud config set project equine-lead

# Verificar
gcloud config get-value project
```

---

## 4. Verificar el remote de DVC

```bash
uv run dvc remote list
# Debe mostrar algo como:
# myremote   gs://equinelead-datalake/...
```

---

## 5. Descargar los datos

```bash
# Descargar todos los datos
uv run dvc pull

# O descargar solo una carpeta específica
uv run dvc pull data/clean
```

---

## 6. Verificar que los datos se descargaron correctamente

```bash
uv run dvc status
# Si todo está OK debe mostrar: "Data and pipelines are up to date."
```

---

## Flujo completo de actualización (cuando hay datos nuevos)

Cuando un compañero suba datos nuevos al bucket y haga `git push`, vos solo necesitás:

```bash
git pull          # bajar los nuevos .dvc pointers
uv run dvc pull   # bajar los datos nuevos desde GCS
```

---

## Troubleshooting

### ❌ `Forbidden: does not have storage.objects.list access`
Tu cuenta no tiene permisos sobre el bucket. Pedile al administrador del proyecto que te agregue con el rol **Storage Object Viewer** en GCS.

### ❌ `VIRTUAL_ENV does not match the project environment path`
Es solo un warning, no afecta el funcionamiento. Podés ignorarlo o usar:
```bash
uv run --active dvc pull
```

### ❌ `No DVC remote configured`
```bash
uv run dvc remote list   # verificar si hay remote
# Si está vacío, pedile al responsable el comando de configuración
```