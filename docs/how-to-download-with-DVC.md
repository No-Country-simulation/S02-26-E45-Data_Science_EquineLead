# 📦 Gestión de Datasets con DVC + GCS (gcloud + uv)

Este proyecto utiliza **DVC** para el versionado de datasets y **Google Cloud Storage (GCS)** como backend de almacenamiento remoto.

Los datos **NO se almacenan en Git**.  
Se descargan bajo demanda utilizando DVC.

---

## 🧩 Requisitos

Antes de descargar los datasets, necesitás tener instalado:

- Git
- Python 3.9 o superior
- Google Cloud SDK (`gcloud`)
- `uv` (gestor de entornos y dependencias)

---

## ☁️ Instalación de Google Cloud SDK (gcloud)

### 🪟 Windows

1. Descargar el instalador desde:  
   https://cloud.google.com/sdk/docs/install
2. Ejecutar el instalador
3. Asegurarse de marcar la opción **“Add gcloud to PATH”**
4. Abrir una nueva terminal y verificar:

```bash
gcloud version
```

---

### 🐧 Linux

```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud version
```

---

### 🍎 macOS

```bash
brew install --cask google-cloud-sdk
gcloud version
```

---

## 🔐 Autenticación con Google Cloud (OBLIGATORIO)

Cada colaborador debe autenticarse con su **cuenta de Google** que tenga permisos de acceso al bucket de GCS.

```bash
gcloud auth login
gcloud auth application-default login
```

✔️ Las credenciales se guardan localmente  
✔️ No se comparten claves  
✔️ No se sube nada a Git  

📌 DVC utilizará automáticamente estas credenciales.

---

## 🐍 Entorno Python con uv

### Instalar uv (una sola vez por máquina)

```bash
pip install uv
```

Verificar:

```bash
uv --version
```

---

### Crear y sincronizar el entorno

Desde la raíz del proyecto:[text](d:/Cursos/NoCountry/S02-26-E45-Data_Science_EquineLead/data/clean) [text](d:/Cursos/NoCountry/S02-26-E45-Data_Science_EquineLead/data/raw)

```bash
uv venv
uv sync
```

Esto:
- crea el entorno virtual
- instala dependencias desde `pyproject.toml`
- incluye DVC con soporte para GCS

---

### Activar el entorno

**Linux / macOS**
```bash
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
.venv\Scripts\activate
```

---

## 📥 Descargar los datasets

### 1️⃣ Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPO>
```

---

### 2️⃣ Descargar datos con DVC

```bash
dvc pull
```

🎉 Listo.

DVC:
- lee la versión de los datos desde Git
- se autentica vía `gcloud`
- descarga exactamente el dataset correcto desde GCS

---

## 📁 Estructura del proyecto (simplificada)

```text
data/
 ├── .gitignore        # evita que Git trackee datos
 ├── raw/              # gestionado por DVC
 ├── clean/            # gestionado por DVC
 ├── tracking/         # gestionado por Git
 ├── clean.dvc         # puntero a los datos (Git)  
 └── raw.dvc           # puntero a los datos (Git)       
   
.dvc/config            # configuración del remote GCS
```

---

## 🧠 Reglas importantes

- ❌ No subir datos a Git
- ❌ No modificar `.dvc/config`
- ❌ No compartir credenciales de Google
- ✅ Usar siempre `dvc pull` para bajar datos
- ✅ Usar `dvc status` para verificar el estado

---

## 🔄 Actualización de datasets (solo maintainers)

```bash
dvc add data/
git commit -m "Update dataset"
dvc push
```

Esto genera automáticamente una **nueva versión del dataset**.

---

## 🧪 Troubleshooting

### Ver autenticación
```bash
gcloud auth list
```

### Ver estado de DVC
```bash
dvc status
```

### Debug detallado
```bash
dvc pull -v
```

**Errores comunes:**
- `403 Forbidden` → no tenés acceso al bucket
- `401 Unauthorized` → no estás autenticado con gcloud

---

## 🏁 Resumen rápido

Una vez configurado, cualquier colaborador solo necesita ejecutar:

```bash
dvc pull
```

para reproducir exactamente los datos del proyecto.


---

## ⬆️ Subir datasets a GCS usando DVC (solo maintainers)

⚠️ **Esta sección es SOLO para maintainers o data engineers.**  
El resto de colaboradores **NO deben subir datos**.

---

### 1️⃣ Agregar o modificar datos

Colocá o actualizá archivos dentro de la carpeta gestionada por DVC (por ejemplo `data/clean`):

```text
data/
 ├── .gitignore        # evita que Git trackee datos
 ├── raw/              # gestionado por DVC
 ├── clean/            # gestionado por DVC
 ├── tracking/         # gestionado por Git
 ├── clean.dvc         # puntero a los datos (Git)  
 └── raw.dvc           # puntero a los datos (Git)
```

---

### 2️⃣ Trackear los cambios con DVC

```bash
dvc add data/clean
```

Esto:
- calcula hashes de los archivos
- actualiza `clean.dvc`
- NO sube datos todavía

---

### 3️⃣ Versionar los metadatos con Git

```bash
git status
git add clean.dvc data/clean.gitignore
git commit -m "Update dataset version"
```

📌 Git **solo** versiona referencias, nunca los datos reales.

---

### 4️⃣ Subir los datos al remote (GCS)

```bash
dvc push
```

DVC:
- usa las credenciales de `gcloud`
- sube los archivos al bucket GCS
- mantiene versionado completo

---

### 5️⃣ Verificar el estado

```bash
dvc status
```

Si todo está correcto, deberías ver:

```text
Data and pipelines are up to date.
```

---

## 🔄 Flujo recomendado de trabajo

```text
Modificar datos
   ↓
dvc add
   ↓
git commit
   ↓
dvc push
```

📌 **Nunca** hacer `dvc push` sin un commit previo.

---

## 🏷️ Buenas prácticas de versionado

- Usar commits descriptivos:
  ```text
  Update dataset: cleaned null values and fixed schema
  ```
- Opcional: taggear versiones importantes:
  ```bash
  git tag data-v1.0
  git push --tags
  ```

Esto permite reproducir exactamente un experimento en el futuro.