import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.style_utils import apply_pro_chart_style, PRO_COLORS

def render_executive_summary(df_users, df_horses, df_products, df_u_sessions, df_p_sessions):
    st.markdown("<h1>Executive Control Center</h1>", unsafe_allow_html=True)
    st.markdown("Real-time aggregate performance indicators across the EquineLead ecosystem.")
    
    # ROW 1: KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Active Global Users", f"{len(df_users):,}" if not df_users.empty else "0", "12% MoM")
    kpi2.metric("Horses in Marketplace", f"{len(df_horses):,}" if not df_horses.empty else "0", "4.2% MoM")
    kpi3.metric("Retail Products", f"{len(df_products):,}" if not df_products.empty else "0", "8.9% MoM")
    total_sessions = len(df_u_sessions) + len(df_p_sessions)
    kpi4.metric("Total Interacted Sessions", f"{total_sessions:,}", "15.3% MoM")
    st.markdown("<br>", unsafe_allow_html=True)

    # ROW 2: Primary Visuals
    r2_c1, r2_c2 = st.columns([6, 4])
    
    with r2_c1:
        if not df_users.empty and 'first_seen' in df_users.columns:
            Growth = df_users.groupby(df_users['first_seen'].dt.date).size().reset_index(name='Users')
            Growth.columns = ['date', 'Users']
            Growth['Cumulative'] = Growth['Users'].cumsum()
            fig_acq = px.area(Growth, x='date', y='Cumulative', color_discrete_sequence=[PRO_COLORS[0]])
            fig_acq.add_scatter(x=Growth['date'], y=Growth['Users'], mode='lines', name='Daily New', line=dict(color=PRO_COLORS[1], width=2, dash='dot'))
            st.plotly_chart(apply_pro_chart_style(fig_acq, "Cumulative Network Growth vs Daily Acquisition"), use_container_width=True)

    with r2_c2:
        if not df_users.empty and 'traffic_source' in df_users.columns:
            fig_traffic = px.pie(df_users, names='traffic_source', hole=0.6, color_discrete_sequence=PRO_COLORS)
            st.plotly_chart(apply_pro_chart_style(fig_traffic, "Traffic Source Origin"), use_container_width=True)

    # ROW 3: Secondary Visuals
    r3_c1, r3_c2 = st.columns(2)
    with r3_c1:
        if not df_users.empty and 'country' in df_users.columns:
            c_ct = df_users['country'].value_counts().reset_index()
            c_ct.columns = ['Country', 'Users']
            fig_geo = px.choropleth(c_ct, locations='Country', locationmode='country names', color='Users', color_continuous_scale="Blues")
            fig_geo.update_layout(geo=dict(bgcolor="#1A1C24", showland=True, landcolor="#2D3748", showlakes=False))
            st.plotly_chart(apply_pro_chart_style(fig_geo, "Global Penetration Map"), use_container_width=True)
            
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
            st.plotly_chart(apply_pro_chart_style(fig_stack, "Aggregated Platform Usage (Interactions)"), use_container_width=True)
