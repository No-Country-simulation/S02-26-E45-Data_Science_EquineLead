import pandas as pd
from pathlib import Path

PATH_OUTPUT = Path("./data/clean")
PATH_INPUT = Path("./data/raw")
PATH_OUTPUT.mkdir(parents=True, exist_ok=True)

def clean_data(df_prod_clean: pd.DataFrame) -> pd.DataFrame :
    print("--- Starting Product Database Cleaning ---")

    cols_texto = ['Item_ID', 'Name', 'Description']
    cols_links = ['Images', 'URL']

    for col in cols_texto:
        if col in df_prod_clean.columns:
            df_prod_clean[col] = (df_prod_clean[col]
                                .astype(str)
                                .str.lower()
                                .str.strip()
                                .replace({'nan': 'unknown', 'none': 'unknown', 'sin información': 'unknown'}))
    print("✅ Text columns normalized (lowercase & English nans).")

    if 'Price' in df_prod_clean.columns:
        df_prod_clean['Price'] = df_prod_clean['Price'].astype(str).str.replace(r'[$,]', '', regex=True)
        df_prod_clean['Price'] = pd.to_numeric(df_prod_clean['Price'], errors='coerce')
        df_prod_clean['Price'] = df_prod_clean['Price'].fillna(df_prod_clean['Price'].median())

    if 'Stock' in df_prod_clean.columns:
        df_prod_clean['Stock'] = df_prod_clean['Stock'].astype(str).str.extract(r'(\d+)').astype(float)
        df_prod_clean['Stock'] = df_prod_clean['Stock'].fillna(0).astype(int)
    print("✅ Price and Stock converted to numbers.")

    for col in cols_links:
        if col in df_prod_clean.columns:
            df_prod_clean[col] = (df_prod_clean[col]
                                .astype(str)
                                .str.replace(r"[\[\]\'\"]", "", regex=True) # Quitar corchetes
                                .str.strip()
                                .replace({'nan': 'unknown'}))
    print("✅ Links and Images cleaned but case-sensitive preserved.")

    df_prod_clean["Category"] = df_prod_clean["Category"].str.replace("-", " ")

    print("\n--- FINAL PRODUCT REPORT ---")
    print(f"Total rows: {len(df_prod_clean)}")
    print(f"Total nulls: {df_prod_clean.isnull().sum().sum()}")
    return df_prod_clean

if __name__ == "__main__":
    df_prod = pd.read_parquet(PATH_INPUT / "doversaddlery_products_listing.parquet")
    df_prod_clean = clean_data(df_prod_clean=df_prod)
    df_prod_clean.to_parquet(PATH_OUTPUT / "products_listing_limpio.parquet", index=False)