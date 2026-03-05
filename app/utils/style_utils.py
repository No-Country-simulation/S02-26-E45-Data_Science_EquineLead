import streamlit as st

# Professional Color Palette
PRO_COLORS = [
    "#3366FF",
    "#00B8D9",
    "#36B37E",
    "#FFAB00",
    "#FF5630",
    "#6554C0",
    "#00A3BF",
    "#FF8B00",
    "#FF7452",
    "#8777D9",
]


def inject_premium_style():
    """Injects high-contrast professional dark theme CSS."""
    st.markdown(
        """
    <style>
        /* Force Global Theme Colors */
        [data-testid="stAppViewContainer"] {
            background-color: #0E1117 !important;
            color: #FAFAFA !important;
        }

        /* Sidebar Professional Dark Theme */
        [data-testid="stSidebar"] {
            background-color: #1A1C23 !important;
            border-right: 1px solid #2D3748 !important;
        }

        [data-testid="stSidebar"] * {
            color: #FAFAFA !important;
        }

        /* Make the sidebar text pop */
        [data-testid="stSidebarNav"] span {
            color: #FAFAFA !important;
        }

        /* Power BI Metrics - Premium Cards */
        [data-testid="stMetric"] {
            background-color: #1A1C24 !important;
            border: 1px solid #333333 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5) !important;
            margin-bottom: 1rem !important;
        }

        [data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-size: 2.2rem !important;
            font-weight: 800 !important;
        }

        [data-testid="stMetricLabel"] {
            color: #94A3B8 !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
        }

        /* Hide only the Deploy button and right-side Actions */
        [data-testid="stAppDeployButton"], .stDeployButton, .stToolbarActions, #MainMenu, footer {
            display: none !important;
        }

        /* Ensure the sidebar toggle button is ALWAYS visible and contrasting */
        [data-testid="collapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            background-color: #D4AF37 !important; /* Make the arrow standout */
            border-radius: 0 5px 5px 0 !important;
            color: black !important;
        }

        header {
            background-color: transparent !important;
            box-shadow: none !important;
        }

        /* Global Typography */
        h1, h2, h3, h4, h5, h6, p, label {
            color: #FAFAFA !important;
        }

        /* Professional Button Styling */
        div.stButton > button {
            background-color: #1A1C24 !important;
            color: #D4AF37 !important;
            border: 2px solid #D4AF37 !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
            font-weight: 600 !important;
        }

        div.stButton > button:hover {
            background-color: #D4AF37 !important;
            color: #0E1117 !important;
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.4) !important;
        }

        /* Input Widget Styling */
        div[data-testid="stSelectbox"], div[data-testid="stMultiSelect"], div[data-testid="stTextInput"] {
            background-color: #1A1C24 !important;
            border-radius: 8px !important;
        }

        div[data-baseweb="select"], div[data-baseweb="input"] {
            background-color: #1A1C24 !important;
            border: 1px solid #2D3748 !important;
            border-radius: 8px !important;
        }

        div[data-baseweb="select"] *, div[data-baseweb="input"] * {
            color: #FAFAFA !important;
            background-color: transparent !important;
        }

        /* Expanders (Slicers) - High Contrast Fix for Local & Cloud */
        details[data-testid="stExpander"],
        .st-emotion-cache-1h9usn1,
        .st-emotion-cache-1lsfsc6 {
            background-color: #1A1C24 !important;
            border: 1px solid #333333 !important;
            border-radius: 8px !important;
            margin-bottom: 1rem !important;
            overflow: hidden !important;
        }

        details[data-testid="stExpander"] summary,
        .st-emotion-cache-1u3264x,
        summary.e12o48ov4 {
            background-color: #1A1C24 !important;
            color: #D4AF37 !important;
            border-bottom: 1px solid #333333 !important;
        }

        details[data-testid="stExpander"] summary:hover {
            background-color: #2D3748 !important;
        }

        /* Kill white background on inner expander content in Cloud */
        div[data-testid="stExpanderDetails"],
        .st-emotion-cache-pxambx {
            background-color: #1A1C24 !important;
            padding: 1.5rem !important;
            border-top: none !important;
        }

        /* Fix Selectboxes/Multiselects in Cloud */
        div[data-baseweb="select"],
        div[data-baseweb="input"],
        .st-emotion-cache-1p6fhcq,
        .st-emotion-cache-1er6fxc {
            background-color: #1A1C24 !important;
            border: 1px solid #2D3748 !important;
        }

        /* Force dark background on Dataframes and general containers */
        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrame"] > div,
        .st-emotion-cache-1kyx738 {
            background-color: #1A1C24 !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def apply_pro_chart_style(fig, title=""):
    """Applies a dark card-like style to plotly figures."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="#F8FAFC", family="Segoe UI")),
        template="plotly_dark",
        paper_bgcolor="#1A1C24",
        plot_bgcolor="#1A1C24",
        margin=dict(l=40, r=20, t=60, b=40),
        font=dict(color="#94A3B8"),
        xaxis=dict(showgrid=True, gridcolor="#2D3748", zerolinecolor="#2D3748"),
        yaxis=dict(showgrid=True, gridcolor="#2D3748", zerolinecolor="#2D3748"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12),
        ),
        hovermode="closest",
        shapes=[
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                line=dict(color="#2D3748", width=1),
                layer="below",
            )
        ],
    )
    return fig
