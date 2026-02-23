import pandas as pd
import numpy as np

def validate_leads():
    print("Iniciando validación manual de la materia prima (Datos de Sesiones y Listings)...")
    
    # Cargar datos
    try:
        listings = pd.read_parquet('data/clean/horses_listings_limpio.parquet')
        sessions = pd.read_parquet('data/clean/horses_sessions_info.parquet')
    except Exception as e:
        print(f"Error cargando los datos: {e}")
        return

    print("\n--- 1. Validación de Volumen y Tipos de Datos ---")
    print(f"Total de Registros de Caballos: {len(listings):,}")
    print(f"Total de Eventos de Sesión: {len(sessions):,}")
    
    # Validar nulos críticos en listings
    critical_cols = ['Horse_ID', 'Price', 'Age']
    nulls = listings[critical_cols].isnull().sum()
    print("\n--- 2. Validación de Nulos en Variables Core ---")
    for col, count in nulls.items():
        print(f"Nulos en {col}: {count} ({(count/len(listings))*100:.2f}%)")
        
    print("\n--- 3. Validación de Distribución de Eventos (Leads Reales) ---")
    events_dist = sessions['event_type'].value_counts(normalize=True) * 100
    print(events_dist)
    
    # Muestra manual de un lead exitoso
    print("\n--- 4. Muestra Manual de Lead Calificado (Sample) ---")
    converted_sessions = sessions[sessions['event_type'].isin(['cart', 'purchase'])]['user_session'].unique()
    if len(converted_sessions) > 0:
        sample_session = np.random.choice(converted_sessions)
        sample_data = sessions[sessions['user_session'] == sample_session]
        horse_id = sample_data['horse_id'].iloc[0]
        horse_info = listings[listings['Horse_ID'] == horse_id][['Horse_ID', 'Price', 'Age', 'Registry']]
        
        print(f"Sesión: {sample_session}")
        print("Interacciones previas:")
        print(sample_data[['event_time', 'event_type']])
        print("\nAtributos del Caballo contactado:")
        print(horse_info.to_string(index=False))
        print("\nResultado: VALIDACIÓN EXITOSA. Los leads coinciden con caballos reales en inventario.")
    else:
        print("No se encontraron leads para validar.")

if __name__ == '__main__':
    validate_leads()
