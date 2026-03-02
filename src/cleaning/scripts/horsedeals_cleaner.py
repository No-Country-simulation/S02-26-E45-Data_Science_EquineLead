import pandas as pd
import numpy as np
from pathlib import Path

PATH_OUTPUT = Path("./data/clean")
PATH_INPUT = Path("./data/raw")
PATH_OUTPUT.mkdir(parents=True, exist_ok=True)

def clean_data(df_final: pd.DataFrame) -> pd.DataFrame:
    mapa_nombres = {
        'Sex': 'Gender',
        'Height': 'Height (hh)',
        'Description': 'Comments',
        'Discipline': 'Skills'
    }

    cols_texto_todas = [
        'Company Name', 'Shipping', 'Company Profile', 'Color', 
        'Markings', 'Temperament', 'In Foal', 'Comments', 'Skills', 
        'Location', 'Name', 'Gender', 'Breed', 'Horse Profile'
    ]

    reemplazos = {
                'nan': 'unknown',
                'none': 'unknown',
                'sin información': 'unknown',
                'sin informacion': 'unknown',
                'consultar': 'ask seller',
                'no disponible': 'not provided'
            }
    
    hoy = pd.Timestamp.now().normalize()
    cols_fechas = ['Ad Created', 'Last Update']
    cols_maestras = [
        'Horse_ID', 'Breed', 'Name', 'Gender', 'Foal Date', 'In Foal',
        'Height (hh)', 'Weight (lbs)', 'Temperament', 'Ad Created',
        'Last Update', 'Location', 'Price', 'Horse Profile', 'Skills',
        'Comments', 'Shipping', 'Company Name', 'Company Profile', 'Color',
        'Markings'
    ]
    
    df_final = df_final.rename(columns=mapa_nombres)

    for col in cols_texto_todas:
        if col in df_final.columns:
            df_final[col] = df_final[col].fillna('unknown').astype(str).str.lower().str.strip()
            df_final[col] = df_final[col].str.replace(r"[\[\]\'\"]", "", regex=True)
            df_final[col] = df_final[col].replace(reemplazos)

    print("✅ Texto normalizado a Ingles ('unknown').")

    df_final['Price'] = df_final['Price'].astype(str).str.replace(r'[$,]', '', regex=True)
    df_final['Price'] = pd.to_numeric(df_final['Price'], errors='coerce')

    df_final['Height (hh)'] = df_final['Height (hh)'].astype(str).str.replace('hh', '', regex=False, case=False)
    df_final['Height (hh)'] = pd.to_numeric(df_final['Height (hh)'], errors='coerce')

    df_final['Age'] = df_final['Age'].astype(str).str.extract(r'(\d+)').astype(float) 
    if 'Age' in df_final.columns:
        edad_dias = pd.to_timedelta(df_final['Age'] * 365, unit='D')
        df_final['Foal Date'] = (hoy - edad_dias).dt.normalize()

    for col in cols_fechas:
        if col not in df_final.columns:
            df_final[col] = hoy
        else:
            df_final[col] = pd.to_datetime(df_final[col], errors='coerce').fillna(hoy).dt.normalize()

    for col in cols_maestras:
        if col not in df_final.columns:
            df_final[col] = np.nan

    for col in cols_texto_todas:
        if col in df_final.columns:
            df_final[col] = df_final[col].replace('nan', 'unknown').fillna('unknown')

    if df_final['Weight (lbs)'].isnull().all():
        df_final['Weight (lbs)'] = 1100.0
    else:
        df_final['Weight (lbs)'] = df_final['Weight (lbs)'].fillna(1100.0)

    for col in ['Price', 'Height (hh)']:
        df_final[col] = df_final[col].fillna(df_final.groupby('Breed')[col].transform('median'))
        df_final[col] = df_final[col].fillna(df_final[col].median())

    df_entregable = df_final[cols_maestras].copy()

    cols_links = ['Horse Profile', 'Company Profile'] 

    print(f"Restaurando links originales en: {cols_links}...")

    for col in cols_links:
        if col in df.columns and col in df_entregable.columns:
            df_entregable[col] = df[col]
            df_entregable[col] = df_entregable[col].astype(str).str.strip()
            df_entregable[col] = df_entregable[col].replace({'nan': 'unknown', 'None': 'unknown'})

    print("✅ ¡Links restaurados!")

    return df_entregable

if __name__ == "__main__":
    df = pd.read_parquet(PATH_INPUT / "horsedeals_horses_listings.parquet", engine='fastparquet')
    df = clean_data(df_final=df)
    df.to_parquet(PATH_OUTPUT / "horsedeals_horses_listings_limpio.parquet", index=False)