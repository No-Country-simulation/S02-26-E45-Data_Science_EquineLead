import streamlit as st
import pandas as pd
import numpy as np
import os
from typing import Tuple, Optional

def generate_mock_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generates professional mock data if parquets are missing."""
    np.random.seed(42)
    
    # Mock Listings
    n_listings = 5000
    listings_df = pd.DataFrame({
        'Horse_ID': range(n_listings),
        'Price': np.random.lognormal(mean=9, sigma=1, size=n_listings).clip(1000, 150000),
        'Age': np.random.normal(loc=8, scale=3, size=n_listings).clip(1, 25).astype(int),
        'Registry': np.random.choice(['AQHA', 'USTA', 'KWPN', 'Unknown'], n_listings),
        'Location': np.random.choice(['Florida, USA', 'Kentucky, USA', 'Berlin, Germany'], n_listings),
        'Breed': np.random.choice(['Quarter Horse', 'Thoroughbred', 'Arabian'], n_listings),
        'source': 'Simulado'
    })
    
    # Mock Users
    n_users = 10000
    users_df = pd.DataFrame({
        'user_id': [f'U_{i}' for i in range(n_users)],
        'country': np.random.choice(['USA', 'Germany', 'Netherlands', 'Belgium'], n_users),
        'traffic_source': np.random.choice(['organic', 'paid', 'referral'], n_users),
        'source': 'Simulado'
    })
    
    # Mock Sessions
    n_sessions = 50000
    sessions_df = pd.DataFrame({
        'user_id': np.random.choice(users_df['user_id'], n_sessions),
        'user_session': [f'S_{i}' for i in range(n_sessions)],
        'horse_id': np.random.choice(listings_df['Horse_ID'], n_sessions),
        'event_type': np.random.choice(['view', 'cart', 'purchase'], n_sessions, p=[0.85, 0.12, 0.03]),
        'source': 'Simulado'
    })
    
    return listings_df, sessions_df, users_df


@st.cache_data
def load_parquet_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Loads all real datasets. Enriches sessions with ML projections.
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, '..', '..', 'data', 'clean')
        
        path_listings = os.path.join(data_dir, 'horses_listings_limpio.parquet')
        path_sessions = os.path.join(data_dir, 'horses_sessions_info.parquet')
        path_users = os.path.join(data_dir, 'users_info.parquet')
        
        if all(os.path.exists(p) for p in [path_listings, path_sessions, path_users]):
            st.sidebar.success("Auditoría Real: Datasets Conectados ✅")
            listings = pd.read_parquet(path_listings)
            sessions = pd.read_parquet(path_sessions)
            users = pd.read_parquet(path_users)
            
            # Enrich Listings with source tag
            listings['source'] = 'Real'
            sessions['source'] = 'Real'
            users['source'] = 'Real'
            
            # Add ML Projections (Synthetic/Projected) explicitly to sessions
            np.random.seed(42)
            sessions['predicted_prob'] = np.random.beta(a=2, b=5, size=len(sessions))
            sessions['experiment_group'] = np.random.choice(
                ['Control (Static)', 'Treatment (Hook)'], len(sessions)
            )
            
            return listings, sessions, users
        else:
            st.sidebar.warning("Usando Simulated Data (Tolerancia a Fallos) ⚠️")
            return generate_mock_data()
            
    except Exception as e:
        st.sidebar.error(f"Error crítico en I/O. Forzando simulación. {e}")
        return generate_mock_data()
