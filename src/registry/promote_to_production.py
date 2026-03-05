import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from misc.config import init_mlflow
import mlflow

init_mlflow()

client = mlflow.tracking.MlflowClient()

3
def get_model_versions(model_name: str) -> list:
    """Obtiene todas las versiones con sus aliases correctamente cargados"""
    try:
        versions = client.search_model_versions(f"name='{model_name}'")
    except Exception as e:
        raise ValueError(f"No se encontró el modelo {model_name}: {e}")

    if not versions:
        raise ValueError(f"{model_name} no tiene versiones registradas")

    # Recargar cada versión individualmente para obtener los aliases
    versions_with_aliases = [
        client.get_model_version(model_name, v.version)
        for v in versions
    ]

    return versions_with_aliases

def get_version_by_alias(versions: list, alias: str):
    """Retorna la versión que tiene un alias específico, o None si no existe"""
    return next(
        (v for v in versions if alias in (v.aliases or [])),
        None
    )


def get_version_by_number(versions: list, version_number: int):
    """Retorna la versión por número, o None si no existe"""
    return next(
        (v for v in versions if int(v.version) == version_number),
        None
    )


def print_model_status(model_name: str, versions: list, label: str = "Estado"):
    """Imprime el estado actual de todas las versiones del modelo"""
    print(f"\n📋 {label} de {model_name}:")
    for v in sorted(versions, key=lambda v: int(v.version)):
        aliases = v.aliases or []
        print(f"   v{v.version} → {aliases if aliases else 'sin alias'}")


def clear_aliases(model_name: str, version: str):
    """Elimina todos los aliases de una versión específica"""
    v = client.get_model_version(model_name, version)
    for alias in (v.aliases or []):
        client.delete_registered_model_alias(name=model_name, alias=alias)
        print(f"   🗑️  Alias '{alias}' eliminado de {model_name} v{version}")


def archive_version(model_name: str, version: str):
    """Limpia aliases existentes y asigna 'archived' a una versión"""
    clear_aliases(model_name, version)
    client.set_registered_model_alias(name=model_name, alias="archived", version=version)
    print(f"📦 {model_name} v{version} → archived")


def set_production_version(model_name: str, target_version: int):
    """
    Mueve una versión específica a production.
    - La versión actual en production pasa a archived.
    - Las versiones en staging pierden su alias.
    - Solo target_version queda con alias 'production'.
    """
    versions = get_model_versions(model_name)

    target = get_version_by_number(versions, target_version)
    if not target:
        available = sorted([int(v.version) for v in versions])
        print(f"❌ v{target_version} no existe. Versiones disponibles: {available}")
        return

    print_model_status(model_name, versions, label="Estado actual")

    # Archivar la versión actual en production si existe
    current_production = get_version_by_alias(versions, "production")
    if current_production:
        if int(current_production.version) == target_version:
            print(f"\n⚠️  v{target_version} ya está en production, no hay cambios")
            return
        archive_version(model_name, current_production.version)
    else:
        print(f"\n⚠️  No había ninguna versión en production")

    # Limpiar aliases de la versión target antes de promover
    clear_aliases(model_name, str(target_version))

    # Asignar solo 'production'
    client.set_registered_model_alias(
        name=model_name,
        alias="production",
        version=str(target_version),
    )
    print(f"✅ {model_name} v{target_version} → production")

    versions = get_model_versions(model_name)
    print_model_status(model_name, versions, label="Estado final")

if __name__ == "__main__":
    # Mover una versión específica a production
    VERSION = int(input("Que version queres subir a produccion?: "))
    set_production_version("HORSE_P1", target_version=VERSION)
    set_production_version("HORSE_P2", target_version=VERSION)
    set_production_version("PRODS_P1", target_version=VERSION)
    set_production_version("PRODS_P2", target_version=VERSION)

    set_production_version("model_engine", target_version=1)