import streamlit as st
import pandas as pd
import plotly.express as px
from utils.style_utils import apply_pro_chart_style, PRO_COLORS


def render_retail_analytics(df_products):
    st.markdown("<h1>Equestrian Retail Metrics</h1>", unsafe_allow_html=True)
    if not df_products.empty:
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            if "Price" in df_products.columns:
                df_pp = df_products[df_products["Price"] > 0]
                p95 = df_pp["Price"].quantile(0.95)
                df_pp = df_pp[df_pp["Price"] <= p95]
                fig_pp = px.histogram(
                    df_pp, x="Price", nbins=40, color_discrete_sequence=[PRO_COLORS[2]]
                )
                st.plotly_chart(
                    apply_pro_chart_style(fig_pp, "Retail Price Distribution"),
                    use_container_width=True,
                )
        with r1_c2:
            if "Category" in df_products.columns:
                cat_ct = (
                    df_products["Category"].value_counts().nlargest(12).reset_index()
                )
                cat_ct.columns = ["Category", "Count"]
                fig_cat = px.bar(
                    cat_ct,
                    x="Count",
                    y="Category",
                    orientation="h",
                    color="Count",
                    color_continuous_scale="Sunset",
                )
                fig_cat.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(
                    apply_pro_chart_style(fig_cat, "Top Volume Categories"),
                    use_container_width=True,
                )

        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            if "Stock" in df_products.columns:
                df_st = df_products[
                    df_products["Stock"] < df_products["Stock"].quantile(0.95)
                ]
                fig_st = px.histogram(
                    df_st, x="Stock", color_discrete_sequence=[PRO_COLORS[1]]
                )
                st.plotly_chart(
                    apply_pro_chart_style(fig_st, "Inventory Stock Levels"),
                    use_container_width=True,
                )
        with r2_c2:
            if "Category" in df_products.columns and "Price" in df_products.columns:
                top_cats = df_products["Category"].value_counts().nlargest(5).index
                df_pp = df_products[df_products["Price"] > 0]
                p95 = df_pp["Price"].quantile(0.95)
                df_cp = df_products[
                    (df_products["Category"].isin(top_cats))
                    & (df_products["Price"] <= p95)
                    & (df_products["Price"] > 0)
                ]
                fig_cb = px.box(
                    df_cp,
                    x="Category",
                    y="Price",
                    color="Category",
                    color_discrete_sequence=PRO_COLORS,
                )
                st.plotly_chart(
                    apply_pro_chart_style(fig_cb, "Pricing Tiers by Category"),
                    use_container_width=True,
                )

        r3_c1, r3_c2 = st.columns([1, 1])
        with r3_c1:
            if "Price" in df_products.columns and "Stock" in df_products.columns:
                df_pp = df_products[df_products["Price"] > 0]
                p95 = df_pp["Price"].quantile(0.95)
                df_ps = df_products[
                    (df_products["Price"] <= p95)
                    & (df_products["Stock"] < df_products["Stock"].quantile(0.95))
                ].copy()
                df_ps["Price Tier"] = pd.cut(df_ps["Price"], bins=10).astype(str)
                bar_st = df_ps.groupby("Price Tier")["Stock"].mean().reset_index()

                fig_ps = px.bar(
                    bar_st,
                    x="Price Tier",
                    y="Stock",
                    color="Stock",
                    color_continuous_scale="Sunsetdark",
                )
                st.plotly_chart(
                    apply_pro_chart_style(fig_ps, "Average Stock by Price Tier"),
                    use_container_width=True,
                )
        with r3_c2:
            if "Category" in df_products.columns:
                cat_tree = (
                    df_products.groupby("Category").size().reset_index(name="Count")
                )
                fig_tree = px.treemap(
                    cat_tree,
                    path=["Category"],
                    values="Count",
                    color="Count",
                    color_continuous_scale="Purpor",
                )
                fig_tree.update_layout(
                    paper_bgcolor="#1A1C24",
                    plot_bgcolor="#1A1C24",
                    margin=dict(t=50, l=10, r=10, b=10),
                )
                st.plotly_chart(
                    apply_pro_chart_style(fig_tree, "Inventory Tree Map"),
                    use_container_width=True,
                )
