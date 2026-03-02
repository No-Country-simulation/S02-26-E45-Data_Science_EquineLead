from pathlib import Path
import pandas as pd
from collections import Counter, defaultdict
import numpy as np

DATA_DIR_CLEAN = Path("./data/clean")
DATA_DIR_TRACKING = Path("./data/tracking")

SOURCE_CSV=Path(DATA_DIR_TRACKING / "rees/extracted/2020-Apr.csv")
SAMPLE_PARQUET=Path(DATA_DIR_TRACKING / "rees/extracted/2020-Apr_sample.parquet")

USERS_PARQUET=Path(DATA_DIR_CLEAN / "users_info.parquet")
PRODUCTS_PARQUET=Path(DATA_DIR_CLEAN / "products_listing_limpio.parquet")
OUTPUT_PARQUET=Path(DATA_DIR_CLEAN / "prods_sessions_info.parquet")

SEARCH_WEIGHTS = {
    "horse care": 0.22,
    "horse tack equipment": 0.20,
    "horse riding apparel": 0.15,
    "riding boots chaps": 0.12,
    "helmets protective gear": 0.09,
    "horse blankets": 0.08,
    "kids horse riding apparel": 0.05,
    "stable arena supplies": 0.04,
    "new": 0.03,
    "clearance": 0.015,
    "farm dog gear": 0.015,
}

def assign_prods(df_sessions, df_prods, seed=42):
    rng = np.random.default_rng(seed)

    prods_by_cat = (
        df_prods
        .groupby("Category")["Item_ID"]
        .apply(np.array)
        .to_dict()
    )

    def sample_prod(cat):
        return rng.choice(prods_by_cat[cat])

    df_sessions = df_sessions.copy()
    df_sessions["Item_ID"] = df_sessions["product_category"].map(sample_prod)

    return df_sessions

def build_rees_sample(
    source_csv: Path,
    output_parquet: Path,
    col: str,
    chunksize: int,
    target: int,
    random_state: int
) -> pd.DataFrame:

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

def assign_sessions_to_users(df_sessions, users_ids, seed=42):
    rng = np.random.default_rng(seed)
    sessions = df_sessions["user_session"].unique().tolist()

    if len(users_ids) < len(sessions):
        raise ValueError("No hay suficientes users para asignar sesiones")

    rng.shuffle(sessions)
    rng.shuffle(users_ids)

    session_to_user = dict(zip(sessions, users_ids[:len(sessions)]))

    df_sessions = df_sessions.copy()
    df_sessions["user_id"] = df_sessions["user_session"].map(session_to_user)

    return df_sessions



def assign_product_categories(df_sessions, search_weights, seed=42):
    rng = np.random.default_rng(seed)

    weights = pd.Series(search_weights)
    weights = weights / weights.sum()

    N = len(df_sessions)
    counts = (weights * N).astype(int)

    diff = N - counts.sum()
    if diff != 0:
        counts.iloc[0] += diff

    df_sessions = df_sessions.copy()
    df_sessions["product_category"] = ""

    for category, n in counts.items():
        empty = df_sessions[df_sessions["product_category"] == ""]
        sampled = empty.sample(n=n, random_state=seed)
        df_sessions.loc[sampled.index, "product_category"] = category

    return df_sessions

def assign_products(df_sessions, df_products, seed=42):
    rng = np.random.default_rng(seed)

    prods_by_cat = (
        df_products
        .groupby("Category")["Item_ID"]
        .apply(np.array)
        .to_dict()
    )

    all_products = df_products["Item_ID"].dropna().to_numpy()

    def sample_prod(cat):
        if cat in prods_by_cat and len(prods_by_cat[cat]) > 0:
            return rng.choice(prods_by_cat[cat])
        else:
            return rng.choice(all_products)

    df_sessions = df_sessions.copy()
    df_sessions["Item_ID"] = df_sessions["product_category"].map(sample_prod)

    return df_sessions

def build_product_sessions_pipeline(
    source_csv,
    sample_parquet,
    users_parquet,
    products_parquet,
    output_parquet,
    search_weights,
):
    df_sessions = build_rees_sample(
        source_csv=source_csv,
        output_parquet=sample_parquet,
        col="event_type",
        chunksize=200_000,
        target=1_000_000,
        random_state=42
    )

    df_users = pd.read_parquet(users_parquet)
    users_ids = df_users["user_id"].astype(str).tolist()

    df_sessions = assign_sessions_to_users(df_sessions, users_ids)

    df_sessions = assign_product_categories(
        df_sessions,
        search_weights,
    )

    df_products = pd.read_parquet(products_parquet)
    df_products["Category"] = df_products.URL.apply(
        lambda x: x.split("/")[4].replace("-", " ")
    )

    df_sessions = assign_products(df_sessions, df_products)

    df_sessions = df_sessions[
        ["user_id", "user_session", "Item_ID", "event_type", "event_time"]
    ].rename(columns={"Item_ID": "item_id"})

    df_sessions.to_parquet(output_parquet)

    return df_sessions

if __name__ == '__main__':
    build_product_sessions_pipeline(
        source_csv=SOURCE_CSV,
        sample_parquet=SAMPLE_PARQUET,
        users_parquet=USERS_PARQUET,
        products_parquet=PRODUCTS_PARQUET,
        output_parquet=OUTPUT_PARQUET,
        search_weights=SEARCH_WEIGHTS,
    )