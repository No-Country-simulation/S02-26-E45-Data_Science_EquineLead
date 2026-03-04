import streamlit as st
import pandas as pd

def render_global_filters(listings: pd.DataFrame, sessions: pd.DataFrame, users: pd.DataFrame):
    """
    Renders a set of segmenters in the sidebar and returns filtered dataframes.
    Style: Slicers like PowerBI.
    """
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3004/3004022.png", width=50)
    st.sidebar.header("Segmentadores (Slicers)")
    
    # Filter 1: Breed (Raza)
    all_breeds = sorted(listings['Breed'].unique().tolist())
    selected_breeds = st.sidebar.multiselect("Filtrar por Raza", all_breeds, default=[])
    
    # Filter 2: Location (State/Region)
    listings['State'] = listings['Location'].apply(lambda x: x.split(',')[-1].strip().upper() if ',' in str(x) else 'N/A')
    all_states = sorted(listings['State'].unique().tolist())
    selected_states = st.sidebar.multiselect("Filtrar por Región (Estado)", all_states, default=[])

    # Filter 3: Price Range
    min_p = float(listings['Price'].min())
    max_p = float(listings['Price'].max())
    price_range = st.sidebar.slider("Rango de Precio (USD)", min_p, max_p, (min_p, max_p))

    # Apply Filters to Listings
    filtered_listings = listings.copy()
    if selected_breeds:
        filtered_listings = filtered_listings[filtered_listings['Breed'].isin(selected_breeds)]
    if selected_states:
        filtered_listings = filtered_listings[filtered_listings['State'].isin(selected_states)]
    filtered_listings = filtered_listings[(filtered_listings['Price'] >= price_range[0]) & (filtered_listings['Price'] <= price_range[1])]

    # Synchronize Sessions (only show sessions related to filtered horses)
    filtered_sessions = sessions[sessions['horse_id'].isin(filtered_listings['Horse_ID'])]
    
    # Synchronize Users (only show users present in those sessions)
    filtered_users = users[users['user_id'].isin(filtered_sessions['user_id'])] if 'user_id' in filtered_sessions.columns else users

    return filtered_listings, filtered_sessions, filtered_users
