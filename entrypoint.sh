#!/bin/sh
set -e

if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  echo "❌ GOOGLE_APPLICATION_CREDENTIALS no está seteada"
  exit 1
fi

if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  echo "❌ No existe el archivo de credenciales: $GOOGLE_APPLICATION_CREDENTIALS"
  exit 1
fi

echo "✅ Usando credenciales GCP desde: $GOOGLE_APPLICATION_CREDENTIALS"

exec uv run python flows/equinelead_pipeline.py
