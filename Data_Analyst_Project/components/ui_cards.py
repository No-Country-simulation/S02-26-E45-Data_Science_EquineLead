import streamlit as st

def render_kpi_card(title: str, value: str, delta: str = None, help_text: str = None) -> None:
    \"\"\"
    Render a standardized KPI card across the dashboard.
    \"\"\"
    st.metric(label=title, value=value, delta=delta, help=help_text)

def render_alert(message: str, type: str = "info") -> None:
    \"\"\"
    Renders an alert box.
    \"\"\"
    if type == "warning":
        st.warning(message)
    elif type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    else:
        st.info(message)
