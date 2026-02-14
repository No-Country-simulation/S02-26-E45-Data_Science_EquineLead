from pathlib import Path
import os
import requests
import zipfile
import tarfile
import gzip
import shutil
from typing import Literal
from urllib.parse import urlparse
import pandas as pd
from collections import Counter, defaultdict
from faker import Faker
from faker.providers import BaseProvider
import random
from babel import Locale
import pycountry
import numpy as np
import uuid
from datetime import datetime, timedelta

DATA_DIR_CLEAN = Path("./data/clean")
DATA_DIR_TRACKING = Path("./data/tracking")

def download_and_prepare(
    url: str,
    download_path: str,
    extract_dir: str | None = None,
    chunk_size: int = 8192,
    mode: Literal["download", "extract", "download_and_extract"] = "download_and_extract",
) -> None:
    """
    Descarga y/o extrae un archivo desde una URL.

    Soporta:
    - ZIP (.zip)
    - TAR.GZ / TGZ (.tar.gz, .tgz)
    - GZ simple (.gz → un solo archivo)
    - Archivos sin compresión (solo descarga)

    Modes
    -----
    - download: solo descarga
    - extract: solo extrae (el archivo debe existir)
    - download_and_extract: descarga y luego extrae (default)
    """

    download_path = Path(download_path)
    os.makedirs(download_path.parent, exist_ok=True)

    if download_path.suffix == "":
        url_path = Path(urlparse(url).path)
        if url_path.suffix:
            download_path = download_path.with_suffix(url_path.suffix)

    if mode in {"download", "download_and_extract"}:
        if not download_path.exists():
            print(f"Descargando archivo desde {url} ...")
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(download_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)

            print("Descarga completada.")
        else:
            print("El archivo ya existe, no se descargará.")

    if mode not in {"extract", "download_and_extract"}:
        return

    if not download_path.exists():
        raise FileNotFoundError(
            f"No existe el archivo {download_path}. "
            "No se puede extraer."
        )

    is_zip = zipfile.is_zipfile(download_path)
    is_tar = tarfile.is_tarfile(download_path)
    is_gz = download_path.suffix == ".gz" and not is_tar

    if not is_zip and not is_tar and not is_gz:
        print("El archivo no es ZIP, TAR.GZ ni GZ. No se requiere extracción.")
        return

    if extract_dir is None:
        extract_dir = download_path.as_posix() + "_extracted"

    extract_dir = Path(extract_dir)

    if extract_dir.exists():
        print("La carpeta de extracción ya existe, no se descomprimirá.")
        return

    os.makedirs(extract_dir, exist_ok=True)

    if is_zip:
        print("Archivo ZIP detectado. Descomprimiendo...")
        with zipfile.ZipFile(download_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
    elif is_tar:
        print("Archivo TAR.GZ detectado. Descomprimiendo...")
        with tarfile.open(download_path, "r:*") as tar_ref:
            tar_ref.extractall(extract_dir)

    elif is_gz:
        print("Archivo GZ detectado. Descomprimiendo...")

        output_file = extract_dir / download_path.stem  # quita .gz

        with gzip.open(download_path, "rb") as f_in:
            with open(output_file, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        print(f"Archivo extraído: {output_file}")

    print("Archivo descomprimido correctamente.")
    return

class EquestrianJobProvider(BaseProvider):
    def equestrian_job(self):
        equestrian_jobs = []
        with open(DATA_DIR_TRACKING / "equestrian_jobs.txt") as f:
            for line in f:
                if not line.startswith('#'):
                    equestrian_jobs.append(line.strip())
        return random.choice(equestrian_jobs)

def user_info_for_country(country):
    faker = COUNTRY_TO_LOCALE.get(country)
    if faker is None:
        return None

    faker.add_provider(EquestrianJobProvider)
    gender = random.choice(["male", "female"])

    if gender == "male":
        first_name = faker.first_name_male()
    else:
        first_name = faker.first_name_female()

    last_name = faker.last_name()
    name = f"{first_name} {last_name}"
    city = faker.city()
    address = faker.street_address()
    phone = faker.phone_number()
    email = f"{first_name}.{last_name}@{faker.free_email_domain()}".lower()
    credit_card = faker.credit_card_full().split("\n")
    credit_card[1] = name
    credit_card = "\n".join(credit_card)
    job = {
        "title": faker.equestrian_job(),
        "company": faker.company(),
        "suffix": faker.company_suffix()
    }

    return name, gender, email, phone, city, address, credit_card, job

def country_from_locale(locale_str: str):
    locale = Locale.parse(locale_str)

    country_code = locale.territory
    if country_code is None:
        return None

    country = pycountry.countries.get(alpha_2=country_code)
    return country.name if country else None

def generate_users(n_users: int, locales: list):
    devices = ["mobile", "desktop"]
    sources = ["organic", "paid", "referral"]
    base_date = datetime(2020, 1, 1)

    users = []
    for _ in range(n_users):
        user_id = str(uuid.uuid4())
        X = np.random.randint(1, 1800)
        first_seen = base_date - timedelta(days=X)
        country_id = np.random.choice(len(locales))
        country, _ = locales[country_id]
        name, gender, email, phone, city, address, credit_card, job = user_info_for_country(country)
        users.append({
            "user_id": user_id,
            "name": name,
            "gender": gender,
            "country": country, 
            "city": city,
            "addres": address, 
            "credit_card_info": credit_card, 
            "email": email, 
            "phone_number": phone,
            "job_info": job,
            "device_type": np.random.choice(devices, p=[0.6, 0.4]),
            "traffic_source": np.random.choice(sources, p=[0.7, 0.2, 0.1]),
            "first_seen": first_seen.date()
        })

    return pd.DataFrame(users)

def assign_sessions_to_users(df_sessions, users_ids, seed=42):
    rng = np.random.default_rng(seed)
    sessions = df_sessions["user_session"].unique().tolist()

    if len(users_ids) < len(sessions):
        raise ValueError("No hay suficientes users para asignar sesiones")

    rng.shuffle(sessions)
    rng.shuffle(users_ids)

    session_to_user = dict(zip(sessions, users_ids[:len(sessions)]))
    df_sessions["user_id"] = df_sessions["user_session"].map(session_to_user)

    return df_sessions

def assign_horses(df_sessions, df_horses, seed=42):
    rng = np.random.default_rng(seed)

    # Breed -> Horse_IDs
    horses_by_breed = (
        df_horses
        .groupby("Breed")["Horse_ID"]
        .apply(np.array)
        .to_dict()
    )

    # Para cada fila, samplear un Horse_ID válido
    def sample_horse(breed):
        return rng.choice(horses_by_breed[breed])

    df_sessions = df_sessions.copy()
    df_sessions["Horse_ID"] = df_sessions["category_code"].map(sample_horse)

    return df_sessions

def load_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)

def save_parquet(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)

def build_horses_dataset(*paths: Path) -> pd.DataFrame:
    dfs = [pd.read_parquet(p) for p in paths]
    df = pd.concat(dfs, ignore_index=True)
    df["Temperament"] = df["Temperament"].astype("string")
    return df

def load_locales(path: Path) -> list[tuple[str, str]]:
    locales = set()
    with open(path) as f:
        for locale in f:
            locale = locale.strip()
            country = country_from_locale(locale)
            locales.add((country, locale))
    return list(locales)

def build_country_locale_map(locales: list[tuple[str, str]]) -> dict:
    return {country: Faker(locale) for country, locale in locales}

def build_users(n_users: int, locales: list[tuple[str, str]]) -> pd.DataFrame:
    return generate_users(n_users=n_users, locales=locales)

def align_product_to_horse_categories(
    df_sessions: pd.DataFrame,
    df_horses: pd.DataFrame
) -> pd.DataFrame:

    product_dist = df_sessions.category_code.value_counts(normalize=True)
    horse_dist = df_horses.Breed.value_counts(normalize=True)

    product_cats = product_dist.index.tolist()[: len(horse_dist) - 1]
    df_sessions.loc[
        ~df_sessions.category_code.isin(product_cats),
        "category_code"
    ] = "nc"

    product_cats = df_sessions.category_code.value_counts(normalize=True).index.tolist()
    horse_cats = horse_dist.index.tolist()

    mapping = dict(zip(product_cats, horse_cats))
    df_sessions["category_code"] = df_sessions.category_code.map(mapping)

    return df_sessions

def build_horse_sessions(
    df_sessions: pd.DataFrame,
    df_users: pd.DataFrame,
    df_horses: pd.DataFrame,
    seed: int = 42
) -> pd.DataFrame:

    user_ids = df_users["user_id"].astype(str).tolist()
    df_sessions = assign_sessions_to_users(df_sessions, user_ids)

    df_sessions = align_product_to_horse_categories(df_sessions, df_horses)
    df_sessions = assign_horses(df_sessions, df_horses, seed=seed)

    df_sessions = df_sessions[
        ["user_id", "user_session", "Horse_ID", "event_type", "event_time"]
    ].rename(columns={"Horse_ID": "horse_id"})

    return df_sessions

def build_rees_sample(
    source_csv: Path,
    output_parquet: Path,
    col: str,
    chunksize: int,
    target: int,
    random_state: int
) -> pd.DataFrame:

    if output_parquet.exists():
        return pd.read_parquet(output_parquet)

    counts = Counter()
    total = 0

    for chunk in pd.read_csv(source_csv, chunksize=chunksize):
        counts.update(chunk[col].value_counts().to_dict())
        total += len(chunk)

    dist = {k: v / total for k, v in counts.items()}

    target_per_class = {k: int(v * target) for k, v in dist.items()}
    diff = target - sum(target_per_class.values())
    if diff != 0:
        biggest = max(target_per_class, key=target_per_class.get)
        target_per_class[biggest] += diff

    selected = defaultdict(list)

    for chunk in pd.read_csv(source_csv, chunksize=chunksize):

        for cls, n_target in target_per_class.items():
            collected = sum(len(x) for x in selected[cls])
            remaining = n_target - collected

            if remaining <= 0:
                continue

            rows = chunk[chunk[col] == cls]
            if rows.empty:
                continue

            take = min(len(rows), remaining)
            sampled = rows.sample(n=take, random_state=random_state)
            selected[cls].append(sampled)

        total_selected = sum(
            sum(len(x) for x in v) for v in selected.values()
        )

        if total_selected >= target:
            break

    df = pd.concat([pd.concat(v) for v in selected.values()], ignore_index=True)
    df.to_parquet(output_parquet, index=False)

    return df

def build_and_save_horses(
    equinenow_path: Path,
    horsedeals_path: Path,
    output_path: Path
) -> pd.DataFrame:

    df = build_horses_dataset(equinenow_path, horsedeals_path)
    save_parquet(df, output_path)
    return df

def build_locales_and_fakers(locale_file: Path) -> tuple[list, dict]:
    locales = load_locales(locale_file)
    faker_map = build_country_locale_map(locales)
    return locales, faker_map

def set_country_to_locale(faker_map: dict):
    global COUNTRY_TO_LOCALE
    COUNTRY_TO_LOCALE = faker_map

def build_and_save_users(
    n_users: int,
    locales: list,
    output_path: Path
) -> pd.DataFrame:

    df = generate_users(n_users=n_users, locales=locales)
    save_parquet(df, output_path)
    return df

def build_and_save_horse_sessions(
    df_sessions: pd.DataFrame,
    df_users: pd.DataFrame,
    df_horses: pd.DataFrame,
    output_path: Path,
    seed: int = 42
) -> pd.DataFrame:

    df = build_horse_sessions(
        df_sessions=df_sessions,
        df_users=df_users,
        df_horses=df_horses,
        seed=seed
    )

    save_parquet(df, output_path)
    return df

def main():
    download_and_prepare(
        url="https://data.rees46.com/datasets/marketplace/2020-Apr.csv.gz",
        download_path=DATA_DIR_TRACKING / "rees/2020-Apr.csv.gz",
        extract_dir=DATA_DIR_TRACKING / "rees/extracted",
        mode="extract"
    )

    df_sessions = build_rees_sample(
        source_csv=Path(DATA_DIR_TRACKING / "rees/extracted/2020-Apr.csv"),
        output_parquet=Path(DATA_DIR_TRACKING / "rees/extracted/2020-Apr_sample.parquet"),
        col="event_type",
        chunksize=200_000,
        target=1_000_000,
        random_state=42
    )

    df_horses = build_and_save_horses(
        equinenow_path=Path(DATA_DIR_CLEAN / "equinenow_horses_listings_limpio.parquet"),
        horsedeals_path=Path(DATA_DIR_CLEAN / "horsedeals_horses_listings_limpio.parquet"),
        output_path=Path(DATA_DIR_CLEAN / "horses_listings_limpio.parquet")
    )

    locales, faker_map = build_locales_and_fakers(
        Path(DATA_DIR_TRACKING / "locale.txt")
    )
    set_country_to_locale(faker_map)

    df_users = build_and_save_users(
        n_users=200_000,
        locales=locales,
        output_path=Path(DATA_DIR_CLEAN / "users_info.parquet")
    )

    build_and_save_horse_sessions(
        df_sessions=df_sessions,
        df_users=df_users,
        df_horses=df_horses,
        output_path=Path(DATA_DIR_CLEAN / "horses_sessions_info.parquet")
    )

if __name__ == "__main__":
    main()