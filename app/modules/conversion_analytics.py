import streamlit as st
import pandas as pd
import plotly.express as px
from utils.style_utils import apply_pro_chart_style, PRO_COLORS


def render_conversion_analytics(df_u_sessions, df_p_sessions):
    st.markdown("<h1>Funnel & Session Telemetry</h1>", unsafe_allow_html=True)

    # --- POWER BI STYLE SLICERS ---
    with st.expander("🔍 Filter Panel (Slicers)", expanded=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            u_evs = (
                df_u_sessions["event_type"].dropna().unique().tolist()
                if (not df_u_sessions.empty and "event_type" in df_u_sessions.columns)
                else []
            )
            p_evs = (
                df_p_sessions["event_type"].dropna().unique().tolist()
                if (not df_p_sessions.empty and "event_type" in df_p_sessions.columns)
                else []
            )
            all_events = list(set(u_evs + p_evs))
            event_filter = st.multiselect(
                "Select Event Type", options=all_events, default=[]
            )

    filtered_u = df_u_sessions.copy()
    filtered_p = df_p_sessions.copy()
    if event_filter:
        if not filtered_u.empty:
            filtered_u = filtered_u[filtered_u["event_type"].isin(event_filter)]
        if not filtered_p.empty:
            filtered_p = filtered_p[filtered_p["event_type"].isin(event_filter)]

    r1_c1, r1_c2 = st.columns(2)
    with r1_c1:
        if not filtered_u.empty and "event_type" in filtered_u.columns:
            hev = filtered_u["event_type"].value_counts().reset_index()
            hev.columns = ["Event", "Count"]
            fig_he = px.funnel(
                hev,
                x="Count",
                y="Event",
                color="Event",
                color_discrete_sequence=PRO_COLORS,
            )
            st.plotly_chart(
                apply_pro_chart_style(fig_he, "Horse Interaction Funnel"),
                use_container_width=True,
            )
    with r1_c2:
        if not filtered_p.empty and "event_type" in filtered_p.columns:
            pev = filtered_p["event_type"].value_counts().reset_index()
            pev.columns = ["Event", "Count"]
            fig_pe = px.funnel(
                pev,
                x="Count",
                y="Event",
                color="Event",
                color_discrete_sequence=PRO_COLORS[::-1],
            )
            st.plotly_chart(
                apply_pro_chart_style(fig_pe, "Retail Funnel Progression"),
                use_container_width=True,
            )

    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        if not filtered_u.empty and "event_time" in filtered_u.columns:
            filtered_u["date"] = pd.to_datetime(
                filtered_u["event_time"], errors="coerce"
            ).dt.date
            htime = (
                filtered_u.groupby(["date", "event_type"])
                .size()
                .reset_index(name="Count")
            )
            fig_ht = px.bar(
                htime,
                x="date",
                y="Count",
                color="event_type",
                barmode="group",
                color_discrete_sequence=PRO_COLORS,
            )
            st.plotly_chart(
                apply_pro_chart_style(fig_ht, "Horse Event Volume Over Time"),
                use_container_width=True,
            )
    with r2_c2:
        if not filtered_p.empty and "event_time" in filtered_p.columns:
            filtered_p["date"] = pd.to_datetime(
                filtered_p["event_time"], errors="coerce"
            ).dt.date
            ptime = (
                filtered_p.groupby(["date", "event_type"])
                .size()
                .reset_index(name="Count")
            )
            fig_pt = px.bar(
                ptime,
                x="date",
                y="Count",
                color="event_type",
                barmode="group",
                color_discrete_sequence=PRO_COLORS[::-1],
            )
            st.plotly_chart(
                apply_pro_chart_style(fig_pt, "Retail Event Volume Over Time"),
                use_container_width=True,
            )

    r3_c1, r3_c2 = st.columns(2)
    with r3_c1:
        if not filtered_u.empty and "horse_id" in filtered_u.columns:
            top_h = filtered_u["horse_id"].value_counts().nlargest(10).reset_index()
            top_h.columns = ["Horse ID", "Interactions"]
            fig_th = px.bar(
                top_h,
                x="Interactions",
                y="Horse ID",
                orientation="h",
                color_discrete_sequence=[PRO_COLORS[0]],
            )
            fig_th.update_layout(
                yaxis={"categoryorder": "total ascending", "type": "category"}
            )
            st.plotly_chart(
                apply_pro_chart_style(fig_th, "Top 10 High-Velocity Horses"),
                use_container_width=True,
            )
    with r3_c2:
        if not filtered_p.empty and "item_id" in filtered_p.columns:
            top_p = filtered_p["item_id"].value_counts().nlargest(10).reset_index()
            top_p.columns = ["Item ID", "Interactions"]
            fig_tp = px.bar(
                top_p,
                x="Interactions",
                y="Item ID",
                orientation="h",
                color_discrete_sequence=[PRO_COLORS[3]],
            )
            fig_tp.update_layout(
                yaxis={"categoryorder": "total ascending", "type": "category"}
            )
            st.plotly_chart(
                apply_pro_chart_style(fig_tp, "Top 10 High-Velocity Products"),
                use_container_width=True,
            )

    # --- POWER BI STYLE RAW DATA TABLE ---
    st.markdown(
        "<h3 style='color: #00B8D9; margin-top: 2rem;'>Session Data View</h3>",
        unsafe_allow_html=True,
    )
    t1, t2 = st.tabs(["Horse Sessions", "Retail Sessions"])
    with t1:
        st.dataframe(
            filtered_u.drop(columns=["date"], errors="ignore"),
            use_container_width=True,
            height=250,
        )
    with t2:
        st.dataframe(
            filtered_p.drop(columns=["date"], errors="ignore"),
            use_container_width=True,
            height=250,
        )
