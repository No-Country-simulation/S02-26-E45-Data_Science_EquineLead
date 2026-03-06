import pandas as pd
import plotly.express as px
import streamlit as st
from utils.style_utils import PRO_COLORS, apply_pro_chart_style


def render_audience_analytics(df_users):
    st.markdown("<h1>Audience Demographics</h1>", unsafe_allow_html=True)
    if not df_users.empty:
        # --- POWER BI STYLE SLICERS ---
        with st.expander("🔍 Filter Panel (Slicers)", expanded=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                country_filter = st.multiselect(
                    "Select Country",
                    options=df_users["country"].dropna().unique(),
                    default=[],
                )
            with f_col2:
                traffic_filter = st.multiselect(
                    "Select Traffic Source",
                    options=df_users["traffic_source"].dropna().unique(),
                    default=[],
                )

        # Apply Filters
        filtered_users = df_users.copy()
        if country_filter:
            filtered_users = filtered_users[
                filtered_users["country"].isin(country_filter)
            ]
        if traffic_filter:
            filtered_users = filtered_users[
                filtered_users["traffic_source"].isin(traffic_filter)
            ]

        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            if "city" in filtered_users.columns and not filtered_users.empty:
                ci_ct = filtered_users["city"].value_counts().nlargest(15).reset_index()
                ci_ct.columns = ["City", "Users"]
                fig_ci = px.bar(
                    ci_ct,
                    x="Users",
                    y="City",
                    orientation="h",
                    color="Users",
                    color_continuous_scale="Mint",
                )
                fig_ci.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(
                    apply_pro_chart_style(fig_ci, "Hyperlocal: Top 15 Cities"),
                    use_container_width=True,
                )
        with r1_c2:
            if "gender" in filtered_users.columns and not filtered_users.empty:
                fig_ug = px.pie(
                    filtered_users,
                    names="gender",
                    hole=0.5,
                    color_discrete_sequence=[
                        PRO_COLORS[0],
                        PRO_COLORS[4],
                        PRO_COLORS[2],
                    ],
                )
                st.plotly_chart(
                    apply_pro_chart_style(fig_ug, "User Identity Breakdown"),
                    use_container_width=True,
                )

        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            if "device_type" in filtered_users.columns and not filtered_users.empty:
                dev = filtered_users["device_type"].value_counts().reset_index()
                dev.columns = ["Device", "Count"]
                fig_dev = px.bar(
                    dev,
                    x="Device",
                    y="Count",
                    color="Device",
                    color_discrete_sequence=PRO_COLORS,
                )
                st.plotly_chart(
                    apply_pro_chart_style(fig_dev, "Hardware Telemetry"),
                    use_container_width=True,
                )
        with r2_c2:
            if "first_seen" in filtered_users.columns and not filtered_users.empty:
                filtered_users["week"] = (
                    pd.to_datetime(filtered_users["first_seen"], errors="coerce")
                    .dt.to_period("W")
                    .dt.start_time
                )
                w_acq = filtered_users.groupby("week").size().reset_index(name="Users")
                fig_w = px.line(
                    w_acq,
                    x="week",
                    y="Users",
                    markers=True,
                    color_discrete_sequence=[PRO_COLORS[3]],
                )
                fig_w.update_traces(line=dict(width=3))
                st.plotly_chart(
                    apply_pro_chart_style(fig_w, "Weekly Cohort Volume"),
                    use_container_width=True,
                )

        r3_c1, r3_c2 = st.columns([1, 1])
        with r3_c1:
            if "job_info" in filtered_users.columns and not filtered_users.empty:
                ji = (
                    filtered_users["job_info"].value_counts().nlargest(10).reset_index()
                )
                ji.columns = ["Job Title", "Count"]
                fig_ji = px.bar(
                    ji,
                    x="Count",
                    y="Job Title",
                    orientation="h",
                    color_discrete_sequence=[PRO_COLORS[7]],
                )
                fig_ji.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(
                    apply_pro_chart_style(fig_ji, "Professional Verticals"),
                    use_container_width=True,
                )
        with r3_c2:
            if (
                "country" in filtered_users.columns
                and "traffic_source" in filtered_users.columns
                and not filtered_users.empty
            ):
                sun = (
                    filtered_users.groupby(["country", "traffic_source"])
                    .size()
                    .reset_index(name="Count")
                )
                top5 = filtered_users["country"].value_counts().nlargest(5).index
                sun = sun[sun["country"].isin(top5)]
                if not sun.empty:
                    fig_sun = px.sunburst(
                        sun,
                        path=["country", "traffic_source"],
                        values="Count",
                        color="country",
                        color_discrete_sequence=PRO_COLORS,
                    )
                    fig_sun.update_layout(margin=dict(t=50, l=10, r=10, b=10))
                    st.plotly_chart(
                        apply_pro_chart_style(fig_sun, "Traffic Flow by Top Regions"),
                        use_container_width=True,
                    )

        # --- POWER BI STYLE RAW DATA TABLE ---
        st.markdown(
            "<h3 style='color: #00B8D9; margin-top: 2rem;'>Audience Data View</h3>",
            unsafe_allow_html=True,
        )
        st.dataframe(
            filtered_users.drop(columns=["week"], errors="ignore"),
            use_container_width=True,
            height=250,
        )
