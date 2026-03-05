# 🚀 Manual Definitivo de Despliegue: EquineLead Executive Dashboard

---

## 📑 Tabla de Contenidos del Despliegue Estratégico

1. [Visión General de la Infraestructura](#1-visión-general-de-la-infraestructura)
2. [Arquitectura de Despliegue](#2-arquitectura-de-despliegue)
3. [Entorno de Producción Oficial](#3-entorno-de-producción-oficial)
4. [Guía de Despliegue Local (Paso a Paso)](#4-guía-de-despliegue-local-paso-a-paso)
   - [4.1. Configuración de Entornos Virtuales](#41-configuración-de-entornos-virtuales)
   - [4.2. Instalación de Dependencias Críticas](#42-instalación-de-dependencias-críticas)
   - [4.3. Variables de Entorno y Secretos](#43-variables-de-entorno-y-secretos)
   - [4.4. Ejecución del Servidor Streamlit](#44-ejecución-del-servidor-streamlit)
5. [Despliegue en Streamlit Community Cloud (Guía Definitiva)](#5-despliegue-en-streamlit-community-cloud-guía-definitiva)
6. [Despliegue Alternativo Mediante Docker](#6-despliegue-alternativo-mediante-docker)
7. [Integración Continua (CI/CD) con GitHub Actions](#7-integración-continua-cicd-con-github-actions)
8. [Resolución de Problemas (Troubleshooting Avanzado)](#8-resolución-de-problemas-troubleshooting-avanzado)
9. [Optimización de Rendimiento y Memoria](#9-optimización-de-rendimiento-y-memoria)
10. [Políticas de Seguridad y Acceso](#10-políticas-de-seguridad-y-acceso)

---

## 1. Visión General de la Infraestructura

El **EquineLead Executive Dashboard** no es una simple página web; es el producto final de un complejo ecosistema de Ingeniería de Datos y Machine Learning. Este documento detalla exhaustivamente cómo llevar este motor analítico de 20 gráficos y simuladores estocásticos interactivos desde un código base local hasta un entorno de producción de alta disponibilidad.

El objetivo principal de este despliegue es asegurar que los analistas financieros, científicos de datos y directivos (Stakeholders) tengan acceso con latencia mínima (<200ms) a las visualizaciones de ROI, Inferencia Causal, y Machine Learning en cualquier parte del mundo.

---

## 2. Arquitectura de Despliegue

La aplicación está diseñada para ser agnóstica a la infraestructura gracias a su refactorización reciente hacia la carpeta `app/`. La arquitectura de despliegue sigue estos principios:

- **Estructura Modular:** Todos los archivos críticos de la aplicación se centralizan en `app/`.
- **Fault Tolerance:** El módulo `utils/data_loader.py` permite arrancar la aplicación incluso si la base de datos de producción colapsa, usando datos in-memory (Mock Data).
- **Manejo de Caché:** Uso extensivo del decorador `@st.cache_data` para evitar recálculos en la capa de interfaz.

```mermaid
graph TD
    A[Repositorio GitHub] -->|Git Push| B(Streamlit Cloud Server)
    A -->|Docker Build| C[Docker Hub / GCR]
    C -->|Pull| D[GCP Run / AWS ECS]
    B --> E{Capa de Presentación UI}
    E --> F((Módulo 1: Data Eng))
    E --> G((Módulo 2: Core Biz))
    E --> H((Módulo 3: ML))
    E --> I((Módulo 4: Causal))
    E --> J((Módulo 5: ROI))
```

---

## 3. Entorno de Producción Oficial

La versión certificada y estable del dashboard se encuentra siempre disponible en línea, sin necesidad de instalaciones locales. Este es el entorno de referencia para todas las demostraciones ejecutivas.

🔥 **[ACCESO AL DASHBOARD OFICIAL EN STREAMLIT CLOUD](https://s02-26-e45-datascienceequinelead-amho5xwvihnuxgejqidpxn.streamlit.app/)** 🔥

Este entorno cuenta con:
- Actualizaciones automáticas (Continuous Deployment) con cada commit en la rama `data_analyst`.
- Gestión de memoria optimizada por los servidores de Streamlit.
- Configuración automática del tema oscuro (Dark Mode) y paleta de colores corporativa.

---

## 4. Guía de Despliegue Local (Paso a Paso)

Para desarrolladores, data scientists, o analistas que necesiten alterar gráficos, agregar nuevos KPIs o modificar algoritmos, la ejecución local es obligatoria.

### 4.1. Configuración de Entornos Virtuales

Es imperativo aislar las dependencias del proyecto del sistema global de Python para evitar el temido "Dependency Hell". Recomendamos encarecidamente `uv` por su extremada velocidad, o alternativamente `venv`/`conda`.

**Usando UV (Recomendado):**
```bash
# Instalar uv si no se tiene
pip install uv

# Crear entorno virtual ultra rápido
uv venv .venv

# Activar en Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Activar en Linux/Mac
source .venv/bin/activate
```

**Usando Venv Tradicional:**
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
```

### 4.2. Instalación de Dependencias Críticas

Toda la aplicación se nutre de la carpeta `app/`. El archivo `requirements.txt` se ubica allí. Este archivo contiene paquetes pesados destinados a cálculo científico (Numpy, SciPy) y visualización gráfica avanzada (Plotly, Streamlit, Matplotlib).

```bash
# Asegúrate de estar en la raíz de S02-26-E45-Data_Science_EquineLead
# Instalar las librerías al entorno:
pip install -r app/requirements.txt
```

*Nota para sistemas MacOS ARM (M1/M2/M3):* Si tienes problemas compilando `scipy`, utiliza `conda install scipy` antes de ejecutar el requerimiento de pip.

### 4.3. Variables de Entorno y Secretos

El dashboard está diseñado para funcionar en modo local con 'Mock Data' si no detecta bases de datos. Sin embargo, si deseas conectar la interfaz local al Data Lake GCP real, debes crear la carpeta secreta de Streamlit:

1. Crea una carpeta `.streamlit` en la raíz (si no existe).
2. Crea el archivo `.streamlit/secrets.toml`.
3. Añade tus credenciales de Google Cloud (esto no debe subirse a Git bajo ningún concepto):
   ```toml
   [gcp]
   type = "service_account"
   project_id = "equinelead-391219"
   private_key_id = "xxxxxxxxxxxxxxxxxxxxx"
   private_key = "-----BEGIN PRIVATE KEY-----\nMIICRQIBADANBgk...\n-----END PRIVATE KEY-----\n"
   client_email = "admin-data@equinelead.iam.gserviceaccount.com"
   client_id = "11111111111"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   ```

### 4.4. Ejecución del Servidor Streamlit

El comando maestro para invocar al motor de renderizado es el siguiente. Al ejecutarlo, Streamlit montará un servidor Tornado local de alto rendimiento.

```bash
# Lanzar la aplicación apuntando a la entrada en la carpeta app/
streamlit run app/app.py
```

El servidor te responderá en la terminal indicando los puertos:
```text
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.15:8501
```

Presiona `Ctrl + C` en tu consola cuando desees apagar el servidor.

---

## 5. Despliegue en Streamlit Community Cloud (Guía Definitiva)

Si has forkeado el repositorio y deseas tener tu propia URL pública (ejemplo: `tu-nombre-equinelead.streamlit.app`), sigue estos pasos de Arquitectura en la Nube:

1. Visita [share.streamlit.io](https://share.streamlit.io/) e inicia sesión vinculando tu cuenta de GitHub.
2. Haz clic en **"New app"**.
3. Selecciona tu repositorio (ej: `tu-usuario/S02-26-E45-Data_Science_EquineLead`).
4. En **Branch**, selecciona `data_analyst` (o `main` si ya has hecho el merge).
5. **CRÍTICO - Main file path:** Debes indicarle a la nube la nueva ruta estructural. Escribe exactamente:
   `app/app.py`
6. En la sección *Advanced Settings*, selecciona la versión de Python recomendada (Python 3.12+).
7. Haz clic en **Deploy!**

La plataforma construirá el entorno, leerá el `app/requirements.txt` automáticamente (gracias a la inteligencia de descubrimiento de paquetería de Streamlit), y lanzará tu entorno.

---

## 6. Despliegue Alternativo Mediante Docker

Para infraestructuras corporativas rígidas que no usan Streamlit Cloud (por ejemplo, despliegues On-Premise o en Kubernetes), el dashboard es completamente "Dockerizable".

**Paso 1: Crear un `Dockerfile` en el directorio `app/`**
*(Nota: Actualmente esto se puede manejar desde la raíz)*
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del OS necesarias para compilar algun paquete si hace falta
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copiar el contexto
COPY . .

# Instalar requerimientos del Dashboard
RUN pip install --no-cache-dir -r app/requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Paso 2: Construir y correr la imagen:**
```bash
docker build -t equinelead-dashboard:latest .
docker run -p 8501:8501 equinelead-dashboard:latest
```

---

## 7. Integración Continua (CI/CD) con GitHub Actions

Para asegurar que ningún analista rompa la aplicación al subir código, se recomienda tener un Linter. Si quieres configurar un Action, añade `.github/workflows/streamlit_check.yml`:

```yaml
name: Streamlit Code Check
on:
  push:
    branches: [ "data_analyst" ]
  pull_request:
    branches: [ "data_analyst" ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python 3.12
      uses: actions/setup-python@v4
      with:
        python-version: "3.12"
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r app/requirements.txt
    - name: Run Syntax check
      run: |
        python -m py_compile app/app.py
        # Opcionalmente, agregar pytest si se añaden tests unitarios
```

---

## 8. Resolución de Problemas (Troubleshooting Avanzado)

En entornos de alto nivel de estrés (con data frames de 5 Millones de filas), pueden ocurrir errores. A continuación las soluciones para Data Analysts nivel L3.

### Problema A: `ModuleNotFoundError: No module named 'pages'`
**Causa:** La refactorización a la carpeta `app/` alteró el Python Path.
**Solución Inmediata:** Asegúrate de ejecutar `streamlit run app/app.py` desde la raíz absoluta del repositorio, NO entrar con `cd app` y correr `streamlit run app.py` (pues perderás el contexto hacia el `data/` o `utils/`).

### Problema B: Error de Consumo de Memoria (`MemoryError`)
**Causa:** Cargas excesivas de Parquets al entorno local. Streamlit recarga la app completa en cada interacción UI (slider, botón).
**Solución:** Los Data Analysts de este proyecto han implementado `st.cache_data`. Si estás alterando una función de Pandas gruesa en `utils/data_loader.py`, asegúrate que tenga el decorador:
```python
import streamlit as st
import pandas as pd

@st.cache_data(ttl=3600)  # Limpiar cache en 1 hora
def fetch_heavy_data():
    return pd.read_parquet("massive_file.parquet")
```

### Problema C: Los gráficos Plotly no se adaptan al Dark Mode
**Causa:** Por defecto, Plotly inyecta su propio template (ej: fondo blanco).
**Solución:** En el módulo `components/charts.py`, se debe pasar el parámetro `theme="streamlit"` a la figura:
```python
fig.update_layout(template="plotly_dark") # o confiar en el puente automático de Streamlit
st.plotly_chart(fig, use_container_width=True, theme="streamlit")
```

---

## 9. Optimización de Rendimiento y Memoria

Para garantizar un funcionamiento sin fricciones simulando comportamientos de ROI masivos, se aplican las siguientes reglas oro en el código fuente de `app/`:

1.  **Lazy Loading de Páginas:** La arquitectura multi-página de Streamlit (la carpeta `pages/`) garantiza que el código del Simulador ROI (`5_ROI_Simulator.py`) solo consuma RAM y CPU de Python cuando el usuario hace explícitamente clic en esa pestaña.
2.  **Evitar For Loops Puros en Pandas:** En los experimentos causales, todas las operaciones de Data Science se hacen de manera vectorial (usando `np.where`, operaciones `.apply` vectorizadas, o GroupBys en serie de C). El dashboard no puede iterar fila por fila en tiempo de ejecución.
3.  **Compresión Arrow:** Internamente, Streamlit utiliza Apache Arrow IPC Format para transportar la data entre el Backend (Python) y el Frontend (React.js). Los DataFrames deben mantenerse "flacos" (eliminar columnas que el gráfico no usará antes de llamar a `st.dataframe` o `st.plotly_chart`).

---

## 10. Políticas de Seguridad y Acceso

Dado que el dashboard expone algoritmos de IA de código propietario, Inferencia Causal estratégica y proyecciones de Costo por Lead (CPL):
- Proteger el entorno mediante OAuth 2.0 en caso de desplegarse en AWS o GCP a través del Load Balancer Frontal.
- Si se usa *Streamlit Community Cloud* en modalidad privada corporativa, invitar solo a Stakeholders usando el panel de "Share" y verificando correos electrónicos corporativos.
- Nunca commitear variables API Keys a la carpeta `app/`. Utilizar el módulo de Secrets management local (`.streamlit/secrets.toml`) y el dashboard de Secrets de Streamlit Console en producción.

---
**Documento Creado y Certificado por el Equipo de Data Science & Cloud Architecture.**
*EquineLead - Masterpiece Repository | Confidencialidad: Interna / Pública para Revisoría Técnica.*
