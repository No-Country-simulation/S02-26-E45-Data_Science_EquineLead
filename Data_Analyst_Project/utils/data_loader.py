import streamlit as st
import pandas as pd
import numpy as np
import os
from typing import Tuple, Optional, List

def generate_mock_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generates professional mock data if parquets are missing."""
    np.random.seed(42)
    
    # Mock Listings
    n = 5000
    df_horses = pd.DataFrame({
        'Breed': np.random.choice(['Quarter Horse', 'Thoroughbred', 'Arabian'], n),
        'Gender': np.random.choice(['Stallion', 'Mare', 'Gelding'], n),
        'Color': np.random.choice(['Bay', 'Grey', 'Black'], n),
        'Price': np.random.lognormal(mean=9, sigma=1, size=n).clip(1000, 150000),
        'Age': np.random.normal(loc=8, scale=3, size=n).clip(1, 25).astype(int),
        'Location': np.random.choice(['Florida, USA', 'Kentucky, USA', 'Berlin, Germany'], n)
    })
    
    df_products = pd.DataFrame({
        'Category': np.random.choice(['Saddles', 'Bridles', 'Boots'], n),
        'Price': np.random.uniform(50, 500, n),
        'Stock': np.random.randint(0, 100, n)
    })

    df_users = pd.DataFrame({
        'first_seen': pd.date_range(start='2024-01-01', periods=n, freq='H'),
        'country': np.random.choice(['USA', 'Germany', 'Netherlands'], n),
        'city': np.random.choice(['Miami', 'Berlin', 'Amsterdam'], n),
        'traffic_source': np.random.choice(['organic', 'paid', 'referral'], n),
        'gender': np.random.choice(['M', 'F', 'O'], n),
        'device_type': np.random.choice(['Mobile', 'Desktop', 'Tablet'], n),
        'job_info': 'Professional'
    })

    df_sessions = pd.DataFrame({
        'event_time': pd.date_range(start='2024-01-01', periods=n, freq='15min'),
        'event_type': np.random.choice(['view', 'cart', 'purchase'], n),
        'horse_id': np.random.randint(1, 1000, n),
        'item_id': np.random.randint(1, 1000, n)
    })
    
    return df_horses, df_products, df_users, df_sessions

@st.cache_data(show_spinner=False)
def load_data(filename: str, cols: List[str] = None, sample_limit: int = None) -> pd.DataFrame:
    """Optimized data loader with column pruning and cloud-safe engine settings."""
    # Data directory relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "data", "clean"))
    path = os.path.join(data_dir, filename)
    
    if os.path.exists(path):
        try:
            # Use pyarrow with mmap=False for cloud stability
            df = pd.read_parquet(path, columns=cols, engine='pyarrow', memory_map=False)
            
            # Universal date conversion
            for date_col in ['first_seen', 'event_time', 'Birthday']:
                if date_col in df.columns:
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Row capping for performance
            if sample_limit and len(df) > sample_limit:
                df = df.sample(n=sample_limit, random_state=42)
            
            return df
        except Exception as e:
            st.sidebar.error(f"Error loading {filename}: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def get_all_dashboard_data():
    """Master orchestrator for data loading with specific column requirements."""
    with st.spinner('Synchronizing Core Engine Data...'):
        df_horses = load_data("horses_listings_limpio.parquet", 
                             cols=['Breed', 'Gender', 'Color', 'Price', 'Age', 'Location'])
        
        df_products = load_data("products_listing_limpio.parquet", 
                               cols=['Category', 'Price', 'Stock'])
        
        df_u_sessions = load_data("horses_sessions_info.parquet", 
                                 cols=['event_time', 'event_type', 'horse_id'], 
                                 sample_limit=50000)
        
        df_p_sessions = load_data("prods_sessions_info.parquet", 
                                 cols=['event_time', 'event_type', 'item_id'], 
                                 sample_limit=50000)
        
        u_cols = ['first_seen', 'country', 'city', 'traffic_source', 'gender', 'device_type', 'job_info']
        df_users = load_data("users_info.parquet", cols=u_cols)
        
        # Post-processing for job_info (dictionary extraction)
        if not df_users.empty and 'job_info' in df_users.columns:
            df_users['job_info'] = df_users['job_info'].apply(lambda x: x.get('title') if isinstance(x, dict) else x)

        # Fallback to mock if critical tables are empty
        if df_horses.empty or df_users.empty:
            st.sidebar.warning("Using Fallback Simulated Data")
            return generate_mock_data()

        return df_horses, df_products, df_users, df_u_sessions, df_p_sessions
