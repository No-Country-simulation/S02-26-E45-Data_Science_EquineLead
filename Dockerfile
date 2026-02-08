FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

# Evitar buffers raros
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar uv
RUN pip install --no-cache-dir uv

# Copiamos archivos de dependencias
COPY pyproject.toml uv.lock .python-version ./

# Instalar dependencias (reproducible)
RUN uv sync --locked

# Copiamos el código de los scrapers
COPY ./src .

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh
RUN mkdir -p /app/data/raw /app/data/clean

ENTRYPOINT ["/entrypoint.sh"]

# docker build -t equine-lead-scraping:latest .

# export GOOGLE_APPLICATION_CREDENTIALS=[PATH_A_TUS_CREDENCIALES]
# docker run --rm -e PIPELINE_MODE=[ingestion, cleaning] -v $GOOGLE_APPLICATION_CREDENTIALS:$GOOGLE_APPLICATION_CREDENTIALS equinelead-prefect
