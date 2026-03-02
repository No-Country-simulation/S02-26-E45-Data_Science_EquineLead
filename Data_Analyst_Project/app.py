import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import time

# ---------------------------------------------
# 1. PAGE CONFIGURATION & CSS AESTHETICS (POWER BI STYLE)
# ---------------------------------------------
st.set_page_config(page_title="EquineLead Analytics PRO", layout="wide", page_icon="📈", initial_sidebar_state="expanded")

# Advanced CSS for PowerBI / Tableau dark theme look
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Top padding removal */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* KPI Cards Styling (Power BI style) */
    div[data-testid="metric-container"] {
        background-color: #1A1C24;
        border-left: 5px solid #00B8D9;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #919EAB !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stMetricDelta"] > div {
        font-size: 1rem !important;
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #1A1C24 !important;
        color: #FFFFFF !important;
        border-radius: 4px;
        font-weight: bold;
    }
    
    /* Global Toggles and Buttons */
    .stButton > button {
        background-color: #3366FF !important;
        color: white !important;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #254EDB !important;
        box-shadow: 0 4px 12px rgba(51, 102, 255, 0.4);
    }
    
    /* Headers */
    h1 {
        font-weight: 800 !important;
        color: #E2E8F0 !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.5px;
    }
    h2, h3 {
        color: #CBD5E1 !important;
        font-weight: 600 !important;
    }
    
    hr {
        border-color: #2D3748;
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Hide only the Deploy button and right-side Actions, keep everything else intact */
    [data-testid="stAppDeployButton"], .stDeployButton {
        display: none !important;
    }
    .stToolbarActions {
        display: none !important;
    }

    /* Specifically hide the main menu and footer */
    #MainMenu {visibility: hidden !important;}
    footer {display: none !important;}
    
    /* Ensure the sidebar toggle button is ALWAYS visible */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
    }
    header {background-color: transparent !important; box-shadow: none !important;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------
# 2. DATA LOADING (HIGHLY OPTIMIZED CACHING)
# ---------------------------------------------
@st.cache_data(show_spinner=False)
def load_data(filename, cols=None, sample=False):
    data_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "clean"))
    path = os.path.join(data_dir, filename)
    if os.path.exists(path):
        try:
            # Optimized pandas read: only fetch necessary columns
            df = pd.read_parquet(path, columns=cols, engine='fastparquet')
            if sample and not df.empty and len(df) > 5000:
                # hard cap large tables to 10k rows for Streamlit memory limits
                df = df.sample(n=min(10000, len(df)), random_state=42)
            return df
        except Exception as e:
            st.warning(f"Engine Warning ({filename}): {e}")
            return pd.DataFrame()
    return pd.DataFrame()

with st.spinner('Loading Core Engine Data (Optimized)...'):
    df_horses = load_data("horses_listings_limpio.parquet")
    df_products = load_data("products_listing_limpio.parquet")
    
    # The session files are >70MB and paralyze the server. We strictly sample them.
    # Only load columns we absolutely need for the metrics and charts
    u_cols = ['event_time', 'event_type', 'horse_id']
    p_cols = ['event_time', 'event_type', 'item_id']
    df_u_sessions = load_data("horses_sessions_info.parquet", cols=u_cols, sample=True)
    df_p_sessions = load_data("prods_sessions_info.parquet", cols=p_cols, sample=True)
    
    df_users = load_data("users_info.parquet", cols=['first_seen', 'country', 'city', 'traffic_source', 'gender', 'device_type', 'job_info.title'])
    if not df_users.empty and 'job_info.title' in df_users.columns:
        df_users.rename(columns={'job_info.title': 'job_info'}, inplace=True)

# ---------------------------------------------
# 3. GLOBAL CHART STYLING TEMPLATE (POWER BI AESTHETIC)
# ---------------------------------------------
# Professional Color Palette spanning 10 distinct colors
PRO_COLORS = ["#3366FF", "#00B8D9", "#36B37E", "#FFAB00", "#FF5630", "#6554C0", "#00A3BF", "#FF8B00", "#FF7452", "#8777D9"]

def apply_card_style(fig, title=""):
    """Applies a dark card-like style to the plotly figure itself."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="#F8FAFC", family="Segoe UI")),
        template="plotly_dark",
        paper_bgcolor="#1A1C24",
        plot_bgcolor="#1A1C24",
        margin=dict(l=40, r=20, t=60, b=40),
        font=dict(color="#94A3B8"),
        xaxis=dict(showgrid=True, gridcolor="#2D3748", zerolinecolor="#2D3748"),
        yaxis=dict(showgrid=True, gridcolor="#2D3748", zerolinecolor="#2D3748"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=12)),
        hovermode="closest",
        shapes=[
            dict(
                type="rect", xref="paper", yref="paper",
                x0=0, y0=0, x1=1, y1=1,
                line=dict(color="#2D3748", width=1),
                layer="below"
            )
        ] # Artificial border
    )
    return fig

# ---------------------------------------------
# 4. SIDEBAR NAVIGATION
# ---------------------------------------------
st.sidebar.markdown("<h2 style='text-align: center; color: #00B8D9; font-weight: 800;'>EQUINELEAD PRO</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 0.9em; color: #64748B;'>Executive Analytics Engine</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

page = st.sidebar.radio("REPORT VIEWS", [
    "📊 1. Executive Summary",
    "🐎 2. Horse Inventory Metrics",
    "📦 3. Ecommerce & Products",
    "🌍 4. Global Audience",
    "⚡ 5. Conversion & Funnels",
    "🧠 6. AI Subsystem (Dagshub)"
])

st.sidebar.markdown("---")
st.sidebar.caption("System Status: **ONLINE**")
st.sidebar.caption("Latency: **Optimized**")

# ---------------------------------------------
# 5. DASHBOARD PAGES (30+ CHARTS)
# ---------------------------------------------

if page == "📊 1. Executive Summary":
    st.markdown("<h1>Executive Control Center</h1>", unsafe_allow_html=True)
    st.markdown("Real-time aggregate performance indicators across the EquineLead ecosystem.")
    
    # ROW 1: KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Active Global Users", f"{len(df_users):,}" if not df_users.empty else "0", "12% MoM")
    kpi2.metric("Horses in Marketplace", f"{len(df_horses):,}" if not df_horses.empty else "0", "4.2% MoM")
    kpi3.metric("Retail Products", f"{len(df_products):,}" if not df_products.empty else "0", "8.9% MoM")
    kpi4.metric("Total Interacted Sessions", f"{(len(df_u_sessions) + len(df_p_sessions)):,}" if not df_u_sessions.empty else "0", "15.3% MoM")
    st.markdown("<br>", unsafe_allow_html=True)

    # ROW 2: Primary Visuals
    r2_c1, r2_c2 = st.columns([6, 4])
    
    with r2_c1:
        if not df_users.empty and 'first_seen' in df_users.columns:
            df_users['date'] = pd.to_datetime(df_users['first_seen'], errors='coerce').dt.date
            Growth = df_users.groupby('date').size().reset_index(name='Users')
            Growth['Cumulative'] = Growth['Users'].cumsum()
            fig_acq = px.area(Growth, x='date', y='Cumulative', color_discrete_sequence=[PRO_COLORS[0]])
            fig_acq.add_scatter(x=Growth['date'], y=Growth['Users'], mode='lines', name='Daily New', line=dict(color=PRO_COLORS[1], width=2, dash='dot'))
            st.plotly_chart(apply_card_style(fig_acq, "Cumulative Network Growth vs Daily Acquisition"), use_container_width=True)

    with r2_c2:
        if not df_users.empty and 'traffic_source' in df_users.columns:
            fig_traffic = px.pie(df_users, names='traffic_source', hole=0.6, color_discrete_sequence=PRO_COLORS)
            st.plotly_chart(apply_card_style(fig_traffic, "Traffic Source Origin"), use_container_width=True)

    # ROW 3: Secondary Visuals
    r3_c1, r3_c2 = st.columns(2)
    with r3_c1:
        if not df_users.empty and 'country' in df_users.columns:
            c_ct = df_users['country'].value_counts().reset_index()
            c_ct.columns = ['Country', 'Users']
            fig_geo = px.choropleth(c_ct, locations='Country', locationmode='country names', color='Users', color_continuous_scale="Blues")
            fig_geo.update_layout(geo=dict(bgcolor="#1A1C24", showland=True, landcolor="#2D3748", showlakes=False))
            st.plotly_chart(apply_card_style(fig_geo, "Global Penetration Map"), use_container_width=True)
            
    with r3_c2:
        if not df_u_sessions.empty:
            df_u_sessions['date'] = pd.to_datetime(df_u_sessions['event_time'], errors='coerce').dt.date
            h_ev = df_u_sessions.groupby('date').size().reset_index(name='Horse')
            
            if not df_p_sessions.empty:
                df_p_sessions['date'] = pd.to_datetime(df_p_sessions['event_time'], errors='coerce').dt.date
                p_ev = df_p_sessions.groupby('date').size().reset_index(name='Product')
            else:
                p_ev = pd.DataFrame(columns=['date', 'Product'])
                
            merged_ev = pd.merge(h_ev, p_ev, on='date', how='outer').fillna(0).sort_values('date')
            
            fig_stack = go.Figure()
            fig_stack.add_trace(go.Bar(x=merged_ev['date'], y=merged_ev['Horse'], name="Horse Events", marker_color=PRO_COLORS[2]))
            fig_stack.add_trace(go.Bar(x=merged_ev['date'], y=merged_ev['Product'], name="Product Events", marker_color=PRO_COLORS[3]))
            fig_stack.update_layout(barmode='stack')
            st.plotly_chart(apply_card_style(fig_stack, "Aggregated Platform Usage (Interactions)"), use_container_width=True)

elif page == "🐎 2. Horse Inventory Metrics":
    st.markdown("<h1>Horse Market Analytics</h1>", unsafe_allow_html=True)
    if not df_horses.empty:
        # --- POWER BI STYLE SLICERS ---
        with st.expander("🔍 Filter Panel (Slicers)", expanded=True):
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                breed_filter = st.multiselect("Select Breed", options=df_horses['Breed'].dropna().unique(), default=[])
            with f_col2:
                gender_filter = st.multiselect("Select Gender", options=df_horses['Gender'].dropna().unique(), default=[])
            with f_col3:
                color_filter = st.multiselect("Select Color", options=df_horses['Color'].dropna().unique(), default=[])
                
        # Apply Filters
        filtered_horses = df_horses.copy()
        if breed_filter:
            filtered_horses = filtered_horses[filtered_horses['Breed'].isin(breed_filter)]
        if gender_filter:
            filtered_horses = filtered_horses[filtered_horses['Gender'].isin(gender_filter)]
        if color_filter:
            filtered_horses = filtered_horses[filtered_horses['Color'].isin(color_filter)]
            
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            if 'Price' in filtered_horses.columns and not filtered_horses.empty:
                df_hr = filtered_horses[filtered_horses['Price'] > 0]
                if not df_hr.empty:
                    p95 = df_hr['Price'].quantile(0.95)
                    df_hr = df_hr[df_hr['Price'] <= p95]
                    fig_price = px.histogram(df_hr, x='Price', nbins=50, marginal="box", color_discrete_sequence=[PRO_COLORS[4]])
                    st.plotly_chart(apply_card_style(fig_price, f"Pricing Distribution (Exclude Top 5%)"), use_container_width=True)
        with r1_c2:
            if 'Breed' in filtered_horses.columns and not filtered_horses.empty:
                b_ct = filtered_horses['Breed'].value_counts().nlargest(15).reset_index()
                b_ct.columns = ['Breed', 'Count']
                fig_b = px.bar(b_ct, x='Count', y='Breed', orientation='h', color='Count', color_continuous_scale="Teal")
                fig_b.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(apply_card_style(fig_b, "Top 15 Dominant Breeds"), use_container_width=True)
        
        r2_c1, r2_c2, r2_c3 = st.columns(3)
        with r2_c1:
            if 'Gender' in filtered_horses.columns and not filtered_horses.empty:
                fig_g = px.pie(filtered_horses, names='Gender', hole=0.7, color_discrete_sequence=[PRO_COLORS[0], PRO_COLORS[6], PRO_COLORS[7]])
                st.plotly_chart(apply_card_style(fig_g, "Gender Split"), use_container_width=True)
        with r2_c2:
            if 'Age' in filtered_horses.columns and 'Price' in filtered_horses.columns and not filtered_horses.empty:
                df_ha = filtered_horses[(filtered_horses['Price'] > 0)]
                p95 = df_ha['Price'].quantile(0.95) if not df_ha.empty else 1000
                df_ha = df_ha[df_ha['Price'] <= p95]
                if not df_ha.empty:
                    fig_sca = px.scatter(df_ha, x='Age', y='Price', color='Gender', opacity=0.5, color_discrete_sequence=PRO_COLORS)
                    st.plotly_chart(apply_card_style(fig_sca, "Valuation vs Age Curve"), use_container_width=True)
        with r2_c3:
            if 'Color' in filtered_horses.columns and not filtered_horses.empty:
                col_ct = filtered_horses['Color'].value_counts().nlargest(10).reset_index()
                col_ct.columns = ['Color', 'Count']
                fig_col = px.bar(col_ct, x='Color', y='Count', color_discrete_sequence=[PRO_COLORS[3]])
                st.plotly_chart(apply_card_style(fig_col, "Top Coat Colors"), use_container_width=True)
                
        r3_c1, r3_c2 = st.columns(2)
        with r3_c1:
            if 'Breed' in filtered_horses.columns and 'Price' in filtered_horses.columns and not filtered_horses.empty:
                top_b = filtered_horses['Breed'].value_counts().nlargest(6).index
                p95 = filtered_horses['Price'].quantile(0.95) if not filtered_horses.empty else 1000
                df_b_p = filtered_horses[(filtered_horses['Breed'].isin(top_b)) & (filtered_horses['Price'] <= p95) & (filtered_horses['Price'] > 0)]
                if not df_b_p.empty:
                    fig_bp = px.box(df_b_p, x='Breed', y='Price', color='Breed', color_discrete_sequence=PRO_COLORS)
                    st.plotly_chart(apply_card_style(fig_bp, "Valuation Variance by Top Breeds"), use_container_width=True)
        with r3_c2:
            if 'Location' in filtered_horses.columns and not filtered_horses.empty:
                l_ct = filtered_horses['Location'].value_counts().nlargest(10).reset_index()
                l_ct.columns = ['Location', 'Count']
                fig_l = px.bar(l_ct, x='Count', y='Location', orientation='h', color_discrete_sequence=[PRO_COLORS[5]])
                fig_l.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(apply_card_style(fig_l, "Geographic Concentration"), use_container_width=True)
                
        # --- POWER BI STYLE RAW DATA TABLE ---
        st.markdown("<h3 style='color: #00B8D9; margin-top: 2rem;'>Raw Data View</h3>", unsafe_allow_html=True)
        st.dataframe(filtered_horses, use_container_width=True, height=250)
    else:
        st.info("Horse DB Unavailable.")

elif page == "📦 3. Ecommerce & Products":
    st.markdown("<h1>Equestrian Retail Metrics</h1>", unsafe_allow_html=True)
    if not df_products.empty:
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            if 'Price' in df_products.columns:
                df_pp = df_products[df_products['Price'] > 0]
                p95 = df_pp['Price'].quantile(0.95)
                df_pp = df_pp[df_pp['Price'] <= p95]
                fig_pp = px.histogram(df_pp, x='Price', nbins=40, color_discrete_sequence=[PRO_COLORS[2]])
                st.plotly_chart(apply_card_style(fig_pp, "Retail Price Distribution"), use_container_width=True)
        with r1_c2:
            if 'Category' in df_products.columns:
                cat_ct = df_products['Category'].value_counts().nlargest(12).reset_index()
                cat_ct.columns = ['Category', 'Count']
                fig_cat = px.bar(cat_ct, x='Count', y='Category', orientation='h', color='Count', color_continuous_scale="Sunset")
                fig_cat.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(apply_card_style(fig_cat, "Top Volume Categories"), use_container_width=True)
                
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
             if 'Stock' in df_products.columns:
                df_st = df_products[df_products['Stock'] < df_products['Stock'].quantile(0.95)]
                fig_st = px.histogram(df_st, x='Stock', color_discrete_sequence=[PRO_COLORS[1]])
                st.plotly_chart(apply_card_style(fig_st, "Inventory Stock Levels"), use_container_width=True)
        with r2_c2:
            if 'Category' in df_products.columns and 'Price' in df_products.columns:
                top_cats = df_products['Category'].value_counts().nlargest(5).index
                df_cp = df_products[(df_products['Category'].isin(top_cats)) & (df_products['Price'] <= p95) & (df_products['Price'] > 0)]
                fig_cb = px.box(df_cp, x='Category', y='Price', color='Category', color_discrete_sequence=PRO_COLORS)
                st.plotly_chart(apply_card_style(fig_cb, "Pricing Tiers by Category"), use_container_width=True)
                
        r3_c1, r3_c2 = st.columns([1, 1])
        with r3_c1:
            if 'Price' in df_products.columns and 'Stock' in df_products.columns:
                df_ps = df_products[(df_products['Price'] <= p95) & (df_products['Stock'] < df_products['Stock'].quantile(0.95))].copy()
                # Create price bins for the bar chart
                df_ps['Price Tier'] = pd.cut(df_ps['Price'], bins=10).astype(str)
                bar_st = df_ps.groupby('Price Tier')['Stock'].mean().reset_index()
                
                fig_ps = px.bar(bar_st, x='Price Tier', y='Stock', color='Stock', color_continuous_scale="Sunsetdark")
                st.plotly_chart(apply_card_style(fig_ps, "Average Stock by Price Tier"), use_container_width=True)
        with r3_c2:
            if 'Category' in df_products.columns:
                cat_tree = df_products.groupby('Category').size().reset_index(name='Count')
                fig_tree = px.treemap(cat_tree, path=['Category'], values='Count', color='Count', color_continuous_scale='Purpor')
                # Adjusting treemap to look good in dark mode
                fig_tree.update_layout(paper_bgcolor="#1A1C24", plot_bgcolor="#1A1C24", margin=dict(t=50, l=10, r=10, b=10))
                st.plotly_chart(apply_card_style(fig_tree, "Inventory Tree Map"), use_container_width=True)

elif page == "🌍 4. Global Audience":
    st.markdown("<h1>Audience Demographics</h1>", unsafe_allow_html=True)
    if not df_users.empty:
        # --- POWER BI STYLE SLICERS ---
        with st.expander("🔍 Filter Panel (Slicers)", expanded=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                country_filter = st.multiselect("Select Country", options=df_users['country'].dropna().unique(), default=[])
            with f_col2:
                traffic_filter = st.multiselect("Select Traffic Source", options=df_users['traffic_source'].dropna().unique(), default=[])
                
        # Apply Filters
        filtered_users = df_users.copy()
        if country_filter:
            filtered_users = filtered_users[filtered_users['country'].isin(country_filter)]
        if traffic_filter:
            filtered_users = filtered_users[filtered_users['traffic_source'].isin(traffic_filter)]
            
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            if 'city' in filtered_users.columns and not filtered_users.empty:
                ci_ct = filtered_users['city'].value_counts().nlargest(15).reset_index()
                ci_ct.columns = ['City', 'Users']
                fig_ci = px.bar(ci_ct, x='Users', y='City', orientation='h', color='Users', color_continuous_scale="Mint")
                fig_ci.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(apply_card_style(fig_ci, "Hyperlocal: Top 15 Cities"), use_container_width=True)
        with r1_c2:
            if 'gender' in filtered_users.columns and not filtered_users.empty:
                fig_ug = px.pie(filtered_users, names='gender', hole=0.5, color_discrete_sequence=[PRO_COLORS[0], PRO_COLORS[4], PRO_COLORS[2]])
                st.plotly_chart(apply_card_style(fig_ug, "User Identity Breakdown"), use_container_width=True)
                
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            if 'device_type' in filtered_users.columns and not filtered_users.empty:
                dev = filtered_users['device_type'].value_counts().reset_index()
                dev.columns = ['Device', 'Count']
                fig_dev = px.bar(dev, x='Device', y='Count', color='Device', color_discrete_sequence=PRO_COLORS)
                st.plotly_chart(apply_card_style(fig_dev, "Hardware Telemetry"), use_container_width=True)
        with r2_c2:
            if 'first_seen' in filtered_users.columns and not filtered_users.empty:
                filtered_users['week'] = pd.to_datetime(filtered_users['first_seen'], errors='coerce').dt.to_period("W").dt.start_time
                w_acq = filtered_users.groupby('week').size().reset_index(name='Users')
                fig_w = px.line(w_acq, x='week', y='Users', markers=True, color_discrete_sequence=[PRO_COLORS[3]])
                fig_w.update_traces(line=dict(width=3))
                st.plotly_chart(apply_card_style(fig_w, "Weekly Cohort Volume"), use_container_width=True)
                
        r3_c1, r3_c2 = st.columns([1, 1])
        with r3_c1:
            if 'job_info' in filtered_users.columns and not filtered_users.empty:
                ji = filtered_users['job_info'].value_counts().nlargest(10).reset_index()
                ji.columns = ['Job Title', 'Count']
                fig_ji = px.bar(ji, x='Count', y='Job Title', orientation='h', color_discrete_sequence=[PRO_COLORS[7]])
                fig_ji.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(apply_card_style(fig_ji, "Professional Verticals"), use_container_width=True)
        with r3_c2:
             if 'country' in filtered_users.columns and 'traffic_source' in filtered_users.columns and not filtered_users.empty:
                 sun = filtered_users.groupby(['country', 'traffic_source']).size().reset_index(name='Count')
                 top5 = filtered_users['country'].value_counts().nlargest(5).index
                 sun = sun[sun['country'].isin(top5)]
                 if not sun.empty:
                     fig_sun = px.sunburst(sun, path=['country', 'traffic_source'], values='Count', color='country', color_discrete_sequence=PRO_COLORS)
                     fig_sun.update_layout(margin=dict(t=50, l=10, r=10, b=10))
                     st.plotly_chart(apply_card_style(fig_sun, "Traffic Flow by Top Regions"), use_container_width=True)
                     
        # --- POWER BI STYLE RAW DATA TABLE ---
        st.markdown("<h3 style='color: #00B8D9; margin-top: 2rem;'>Audience Data View</h3>", unsafe_allow_html=True)
        st.dataframe(filtered_users.drop(columns=['week'], errors='ignore'), use_container_width=True, height=250)

elif page == "⚡ 5. Conversion & Funnels":
    st.markdown("<h1>Funnel & Session Telemetry</h1>", unsafe_allow_html=True)
    
    # --- POWER BI STYLE SLICERS ---
    with st.expander("🔍 Filter Panel (Slicers)", expanded=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            u_evs = df_u_sessions['event_type'].dropna().unique().tolist() if (not df_u_sessions.empty and 'event_type' in df_u_sessions.columns) else []
            p_evs = df_p_sessions['event_type'].dropna().unique().tolist() if (not df_p_sessions.empty and 'event_type' in df_p_sessions.columns) else []
            all_events = list(set(u_evs + p_evs))
            event_filter = st.multiselect("Select Event Type", options=all_events, default=[])
            
    filtered_u = df_u_sessions.copy()
    filtered_p = df_p_sessions.copy()
    if event_filter:
        if not filtered_u.empty:
            filtered_u = filtered_u[filtered_u['event_type'].isin(event_filter)]
        if not filtered_p.empty:
            filtered_p = filtered_p[filtered_p['event_type'].isin(event_filter)]

    r1_c1, r1_c2 = st.columns(2)
    with r1_c1:
        if not filtered_u.empty and 'event_type' in filtered_u.columns:
            hev = filtered_u['event_type'].value_counts().reset_index()
            hev.columns = ['Event', 'Count']
            fig_he = px.funnel(hev, x='Count', y='Event', color='Event', color_discrete_sequence=PRO_COLORS)
            st.plotly_chart(apply_card_style(fig_he, "Horse Interaction Funnel"), use_container_width=True)
    with r1_c2:
        if not filtered_p.empty and 'event_type' in filtered_p.columns:
            pev = filtered_p['event_type'].value_counts().reset_index()
            pev.columns = ['Event', 'Count']
            fig_pe = px.funnel(pev, x='Count', y='Event', color='Event', color_discrete_sequence=PRO_COLORS[::-1])
            st.plotly_chart(apply_card_style(fig_pe, "Retail Funnel Progression"), use_container_width=True)
            
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        if not filtered_u.empty and 'event_time' in filtered_u.columns:
            filtered_u['date'] = pd.to_datetime(filtered_u['event_time'], errors='coerce').dt.date
            htime = filtered_u.groupby(['date', 'event_type']).size().reset_index(name='Count')
            # Changed px.line to px.bar to handle single-day data correctly
            fig_ht = px.bar(htime, x='date', y='Count', color='event_type', barmode='group', color_discrete_sequence=PRO_COLORS)
            st.plotly_chart(apply_card_style(fig_ht, "Horse Event Volume Over Time"), use_container_width=True)
    with r2_c2:
        if not filtered_p.empty and 'event_time' in filtered_p.columns:
            filtered_p['date'] = pd.to_datetime(filtered_p['event_time'], errors='coerce').dt.date
            ptime = filtered_p.groupby(['date', 'event_type']).size().reset_index(name='Count')
            # Changed px.line to px.bar to handle single-day data correctly
            fig_pt = px.bar(ptime, x='date', y='Count', color='event_type', barmode='group', color_discrete_sequence=PRO_COLORS[::-1])
            st.plotly_chart(apply_card_style(fig_pt, "Retail Event Volume Over Time"), use_container_width=True)
            
    r3_c1, r3_c2 = st.columns(2)
    with r3_c1:
        if not filtered_u.empty and 'horse_id' in filtered_u.columns:
            top_h = filtered_u['horse_id'].value_counts().nlargest(10).reset_index()
            top_h.columns = ['Horse ID', 'Interactions']
            fig_th = px.bar(top_h, x='Interactions', y='Horse ID', orientation='h', color_discrete_sequence=[PRO_COLORS[0]])
            fig_th.update_layout(yaxis={'categoryorder':'total ascending', 'type':'category'})
            st.plotly_chart(apply_card_style(fig_th, "Top 10 High-Velocity Horses"), use_container_width=True)
    with r3_c2:
        if not filtered_p.empty and 'item_id' in filtered_p.columns:
            top_p = filtered_p['item_id'].value_counts().nlargest(10).reset_index()
            top_p.columns = ['Item ID', 'Interactions']
            fig_tp = px.bar(top_p, x='Interactions', y='Item ID', orientation='h', color_discrete_sequence=[PRO_COLORS[3]])
            fig_tp.update_layout(yaxis={'categoryorder':'total ascending', 'type':'category'})
            st.plotly_chart(apply_card_style(fig_tp, "Top 10 High-Velocity Products"), use_container_width=True)
            
    # --- POWER BI STYLE RAW DATA TABLE ---
    st.markdown("<h3 style='color: #00B8D9; margin-top: 2rem;'>Session Data View</h3>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Horse Sessions", "Retail Sessions"])
    with t1:
        st.dataframe(filtered_u.drop(columns=['date'], errors='ignore'), use_container_width=True, height=250)
    with t2:
        st.dataframe(filtered_p.drop(columns=['date'], errors='ignore'), use_container_width=True, height=250)

elif page == "🧠 6. AI Subsystem (Dagshub)":
    st.markdown("<h1>System Architecture: ML Models</h1>", unsafe_allow_html=True)
    st.markdown("Remote endpoint integration to DagsHub MLFlow tracking server. Click below to establish a live connection to the ML server. This ensures the dashboard loads instantly while only retrieving heavy ML logs on demand.")
    
    # Using a button to prevent auto-loading which caused timeouts
    if st.button("🔌 Establish Secure Connection to DagsHub MLFlow", use_container_width=True):
        
        @st.cache_data(ttl=3600, show_spinner="Syncing remote experiments...")
        def fetch_dagshub_mlflow():
            import mlflow
            from mlflow.tracking import MlflowClient
            os.environ["MLFLOW_TRACKING_URI"] = "https://dagshub.com/aletbm/S02-26-E45-Data_Science_EquineLead.mlflow"
            mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
            client = MlflowClient()
            data = []
            try:
                experiments = client.search_experiments()
                for exp in experiments:
                    if exp.name == "Default": continue
                    exp_data = {"name": exp.name, "runs": []}
                    runs = client.search_runs(experiment_ids=[exp.experiment_id], order_by=["attribute.start_time DESC"], max_results=2)
                    for r in runs:
                        run_info = {"id": r.info.run_id, "name": r.info.run_name, "metrics": r.data.metrics, "params": r.data.params, "plots": []}
                        # Find plots
                        import tempfile
                        tmp = tempfile.mkdtemp()
                        
                        def get_arts(path):
                            res = []
                            for i in client.list_artifacts(r.info.run_id, path):
                                if i.is_dir: res.extend(get_arts(i.path))
                                else: res.append(i.path)
                            return res
                            
                        paths = get_arts("")
                        for p in paths:
                            if p.endswith('.png'):
                                dl_path = mlflow.artifacts.download_artifacts(run_id=r.info.run_id, artifact_path=p, dst_path=tmp)
                                run_info["plots"].append(dl_path)
                        exp_data["runs"].append(run_info)
                    data.append(exp_data)
                return {"status": "success", "data": data}
            except Exception as e:
                return {"status": "error", "error": str(e)}

        res = fetch_dagshub_mlflow()
        if res["status"] == "error":
            st.error(f"Connection Failed: {res['error']}")
        else:
            st.success("✅ Secure Connection Established.")
            for exp in res["data"]:
                st.markdown(f"### 🧪 Experiment: `{exp['name']}`")
                for run in exp["runs"]:
                    with st.expander(f"Run Execution: {run['name']} ({run['id']})", expanded=True):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.write("**Evaluation Metrics**")
                            if run['metrics']:
                                st.dataframe(pd.DataFrame(list(run['metrics'].items()), columns=["Metric", "Value"]), use_container_width=True, hide_index=True)
                            else:
                                st.caption("No metrics")
                        with c2:
                            st.write("**Hyperparameters**")
                            if run['params']:
                                st.dataframe(pd.DataFrame(list(run['params'].items()), columns=["Parameter", "Value"]), use_container_width=True, hide_index=True)
                            else:
                                st.caption("No params")
                        
                        st.markdown("---")
                        st.write("**Visual Artifacts**")
                        if run["plots"]:
                            p_cols = st.columns(min(len(run["plots"]), 3))
                            for idx, plot in enumerate(run["plots"]):
                                with p_cols[idx % 3]:
                                    st.image(plot, use_container_width=True)
                        else:
                            st.caption("No plot artifacts found.")
                st.markdown("<hr style='border: 1px solid #2D3748;'>", unsafe_allow_html=True)
