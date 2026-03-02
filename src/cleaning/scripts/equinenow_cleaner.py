import pandas as pd 
import re
import numpy as np
from pathlib import Path

PATH_OUTPUT = Path("./data/clean")
PATH_INPUT = Path("./data/raw")
PATH_OUTPUT.mkdir(parents=True, exist_ok=True)

def tiene_caracteres_raros(texto):
    if pd.isna(texto): return False
    return bool(re.search(r'[^a-zA-Z0-9\s\.\,\-ñÑáéíóúÁÉÍÓÚ]', str(texto)))

def limpieza_extrema(valor):
    texto = str(valor).lower().strip()
    if texto in ['nan', 'unknown', 'sin información', 'none', '']:
        return np.nan
    if '/' in texto:
        parte = texto.split('/')[0].strip()
        try: return float(parte)
        except: return np.nan_to_num
    try:
        solo_num = "".join(filter(str.isdigit, texto))
        return float(solo_num) if solo_num else np.nan
    except:
        return np.nan

def clean_data(df_final: pd.DataFrame) -> pd.DataFrame:
    cols_numericas = ['Price', 'Height (hh)', 'Weight (lbs)']
    cols_fechas = ['Foal Date', 'Ad Created', 'Last Update']
    cols_a_rellenar = ['Price', 'Height (hh)', 'Weight (lbs)', 'Age']
    cols_a_borrar = ['Ad Number', 'Registry Number', 'State Bred']
    cols_links = ['Horse Profile', 'Company Profile'] 
    df_final = df_final.drop(columns=cols_a_borrar, errors='ignore')
    cols_texto = df_final.select_dtypes(include=['object']).columns

    palabras_clave = 'star|blaze|strip|bald|white face|snipe'
    patron_a_mantener = r'[^a-zA-Z0-9\sñÑáéíóúÁÉÍÓÚ\.\,\-\']'
    now = pd.Timestamp.now()

    traduccion = {
        'sin información': 'unknown',
        'sin informacion': 'unknown',
        'no disponible': 'not provided',
        'consultar': 'ask seller',
        'nan': 'unknown',
        'none': 'unknown'
    }
    
    for col in cols_texto:
        df_final[col] = df_final[col].astype(str).str.lower().str.strip()
        df_final[col] = df_final[col].replace({'nan': None, 'none':None, 'sin información': None})

    df_final['Price'] = df_final['Price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)

    for col in cols_numericas:
        df_final[col] = pd.to_numeric(df_final[col], errors='coerce')

    for col in cols_fechas:
        df_final[col] = pd.to_datetime(df_final[col], errors='coerce', format='mixed')
    
    df_final['Age'] = (now - df_final['Foal Date']).dt.days / 365
    df_final['Age'] = df_final['Age'].round(1)

    df_final['Markings'] = df_final['Markings'].fillna('sin información')
    df_final['Has_Face_Markings'] = df_final['Markings'].str.contains(palabras_clave, regex=True).astype(int)

    for col in cols_a_rellenar:
        df_final[col] = df_final[col].fillna(df_final.groupby('Breed')[col].transform('median'))
        df_final[col] = df_final[col].fillna(df_final[col].median())

    df_final['Last Update'] = df_final['Last Update'].fillna(df_final[col].median())

    cols_texto_final = df_final.select_dtypes(include=['object', 'string']).columns
    df_final[cols_texto_final] = df_final[cols_texto_final].fillna('sin información')

    df_final = df_final.drop(columns=['Foal Date'], errors='ignore')

    print("---RESUMEN FINAL---")
    print(f"Total Nulos: {df_final.isnull().sum().sum()}")

    cols_texto = df_final.select_dtypes(include=['object', 'string']).columns

    print("--- Filas con caracteres raros detectados ---")
    for col in cols_texto:
        sucias = df_final[col].apply(tiene_caracteres_raros).sum()
        if sucias > 0:
            print(f"Columna '{col}': {sucias} filas sucias")
            ejemplo = df_final[df_final[col].apply(tiene_caracteres_raros)][col].iloc[0]
            print(f"   Ejemplo: {ejemplo}")

    print("Limpiando asteriscos y emojis... 🧹")
    for col in cols_texto:
        df_final[col] = df_final[col].astype(str).str.replace(patron_a_mantener, '', regex=True) 
        df_final[col] = df_final[col].str.replace(r'\s+', ' ', regex=True).str.strip()

    print("¡Limpieza terminada! ✨")

    cols_texto = df_final.select_dtypes(include=['object', 'string']).columns
    
    print(f"--- Traduciendo {len(cols_texto)} columnas... ---")

    for col in cols_texto:
        df_final[col] = df_final[col].astype(str).str.lower().str.strip()
        df_final[col] = df_final[col].replace(traduccion)

    print("✅ ¡Listo! Todo ahora dice 'unknown'.")

    print(f"Restaurando links originales en: {cols_links}...")

    for col in cols_links:
        if col in df.columns and col in df_final.columns:
            df_final[col] = df[col]
            df_final[col] = df_final[col].astype(str).str.strip()
            df_final[col] = df_final[col].replace({'nan': 'unknown', 'None': 'unknown'})

    print("✅ ¡Links restaurados!")

    if 'Temperament' in df.columns:
        print("🔄 Recuperando datos originales...")
        df_final['Temperament'] = df['Temperament']

        df_final['Temperament'] = df_final['Temperament'].apply(limpieza_extrema)
        promedio_real = df_final['Temperament'].mean()

        if pd.isna(promedio_real):
            print("⚠️ Alerta: ¡Incluso en el original no hay números!")
            promedio_real = 5.0
        else:
            print(f"📊 Promedio real detectado: {round(promedio_real, 2)}")

        df_final['Temperament'] = df_final['Temperament'].fillna(round(promedio_real, 1))

    return df_final

if __name__ == "__main__":
    df = pd.read_parquet(PATH_INPUT / "equinenow_horses_listings.parquet", engine='fastparquet')
    df = clean_data(df_final=df)
    df.to_parquet(PATH_OUTPUT / "equinenow_horses_listings_limpio.parquet", index=False)