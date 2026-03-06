import streamlit as st
import plotly.express as px
from utils.style_utils import apply_pro_chart_style, PRO_COLORS


def render_horse_analytics(df_horses):
    st.markdown("<h1>Horse Market Analytics</h1>", unsafe_allow_html=True)
    if not df_horses.empty:
        # --- POWER BI STYLE SLICERS ---
        with st.expander("🔍 Filter Panel (Slicers)", expanded=True):
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                breed_filter = st.multiselect(
                    "Select Breed",
                    options=df_horses["Breed"].dropna().unique(),
                    default=[],
                )
            with f_col2:
                gender_filter = st.multiselect(
                    "Select Gender",
                    options=df_horses["Gender"].dropna().unique(),
                    default=[],
                )
            with f_col3:
                color_filter = st.multiselect(
                    "Select Color",
                    options=df_horses["Color"].dropna().unique(),
                    default=[],
                )

        # Apply Filters
        filtered_horses = df_horses.copy()
        if breed_filter:
            filtered_horses = filtered_horses[
                filtered_horses["Breed"].isin(breed_filter)
            ]
        if gender_filter:
            filtered_horses = filtered_horses[
                filtered_horses["Gender"].isin(gender_filter)
            ]
        if color_filter:
            filtered_horses = filtered_horses[
                filtered_horses["Color"].isin(color_filter)
            ]

        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            if "Price" in filtered_horses.columns and not filtered_horses.empty:
                df_hr = filtered_horses[filtered_horses["Price"] > 0]
                if not df_hr.empty:
                    p95 = df_hr["Price"].quantile(0.95)
                    df_hr = df_hr[df_hr["Price"] <= p95]
                    fig_price = px.histogram(
                        df_hr,
                        x="Price",
                        nbins=50,
                        marginal="box",
                        color_discrete_sequence=[PRO_COLORS[4]],
                    )
                    st.plotly_chart(
                        apply_pro_chart_style(
                            fig_price, "Pricing Distribution (Exclude Top 5%)"
                        ),
                        use_container_width=True,
                    )
        with r1_c2:
            if "Breed" in filtered_horses.columns and not filtered_horses.empty:
                b_ct = (
                    filtered_horses["Breed"].value_counts().nlargest(15).reset_index()
                )
                b_ct.columns = ["Breed", "Count"]
                fig_b = px.bar(
                    b_ct,
                    x="Count",
                    y="Breed",
                    orientation="h",
                    color="Count",
                    color_continuous_scale="Teal",
                )
                fig_b.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(
                    apply_pro_chart_style(fig_b, "Top 15 Dominant Breeds"),
                    use_container_width=True,
                )

        r2_c1, r2_c2, r2_c3 = st.columns(3)
        with r2_c1:
            if "Gender" in filtered_horses.columns and not filtered_horses.empty:
                fig_g = px.pie(
                    filtered_horses,
                    names="Gender",
                    hole=0.7,
                    color_discrete_sequence=[
                        PRO_COLORS[0],
                        PRO_COLORS[6],
                        PRO_COLORS[7],
                    ],
                )
                st.plotly_chart(
                    apply_pro_chart_style(fig_g, "Gender Split"),
                    use_container_width=True,
                )
        with r2_c2:
            if (
                "Age" in filtered_horses.columns
                and "Price" in filtered_horses.columns
                and not filtered_horses.empty
            ):
                df_ha = filtered_horses[(filtered_horses["Price"] > 0)]
                p95 = df_ha["Price"].quantile(0.95) if not df_ha.empty else 1000
                df_ha = df_ha[df_ha["Price"] <= p95]
                if not df_ha.empty:
                    fig_sca = px.scatter(
                        df_ha,
                        x="Age",
                        y="Price",
                        color="Gender",
                        opacity=0.5,
                        color_discrete_sequence=PRO_COLORS,
                    )
                    st.plotly_chart(
                        apply_pro_chart_style(fig_sca, "Valuation vs Age Curve"),
                        use_container_width=True,
                    )
        with r2_c3:
            if "Color" in filtered_horses.columns and not filtered_horses.empty:
                col_ct = (
                    filtered_horses["Color"].value_counts().nlargest(10).reset_index()
                )
                col_ct.columns = ["Color", "Count"]
                fig_col = px.bar(
                    col_ct,
                    x="Color",
                    y="Count",
                    color_discrete_sequence=[PRO_COLORS[3]],
                )
                st.plotly_chart(
                    apply_pro_chart_style(fig_col, "Top Coat Colors"),
                    use_container_width=True,
                )

        r3_c1, r3_c2 = st.columns(2)
        with r3_c1:
            if (
                "Breed" in filtered_horses.columns
                and "Price" in filtered_horses.columns
                and not filtered_horses.empty
            ):
                top_b = filtered_horses["Breed"].value_counts().nlargest(6).index
                p95 = (
                    filtered_horses["Price"].quantile(0.95)
                    if not filtered_horses.empty
                    else 1000
                )
                df_b_p = filtered_horses[
                    (filtered_horses["Breed"].isin(top_b))
                    & (filtered_horses["Price"] <= p95)
                    & (filtered_horses["Price"] > 0)
                ]
                if not df_b_p.empty:
                    fig_bp = px.box(
                        df_b_p,
                        x="Breed",
                        y="Price",
                        color="Breed",
                        color_discrete_sequence=PRO_COLORS,
                    )
                    st.plotly_chart(
                        apply_pro_chart_style(
                            fig_bp, "Valuation Variance by Top Breeds"
                        ),
                        use_container_width=True,
                    )
        with r3_c2:
            if "Location" in filtered_horses.columns and not filtered_horses.empty:
                l_ct = (
                    filtered_horses["Location"]
                    .value_counts()
                    .nlargest(10)
                    .reset_index()
                )
                l_ct.columns = ["Location", "Count"]
                fig_l = px.bar(
                    l_ct,
                    x="Count",
                    y="Location",
                    orientation="h",
                    color_discrete_sequence=[PRO_COLORS[5]],
                )
                fig_l.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(
                    apply_pro_chart_style(fig_l, "Geographic Concentration"),
                    use_container_width=True,
                )

        # --- POWER BI STYLE RAW DATA TABLE ---
        st.markdown(
            "<h3 style='color: #00B8D9; margin-top: 2rem;'>Raw Data View</h3>",
            unsafe_allow_html=True,
        )
        st.dataframe(filtered_horses, use_container_width=True, height=250)
    else:
        st.info("Horse DB Unavailable.")
