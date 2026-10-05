from pathlib import Path

import pandas as pd
import streamlit as st

from app_pages.common import (
    REQUIRED,
    build_features,
    detect_anomalies,
    load_default,
    render_styles,
)

st.set_page_config(
    page_title="ExpenseGuard AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
render_styles()

st.sidebar.markdown("## ◈ ExpenseGuard AI")
st.sidebar.caption("Small-business expense anomaly intelligence")

page = st.navigation(
    {
        "Workspace": [
            st.Page("app_pages/overview.py", title="Overview", icon=":material/dashboard:"),
            st.Page("app_pages/transactions.py", title="Transactions", icon=":material/receipt_long:"),
        ],
        "Analysis": [
            st.Page("app_pages/anomaly_review.py", title="Anomaly Review", icon=":material/flag:"),
            st.Page("app_pages/insights.py", title="Insights", icon=":material/insights:"),
        ],
        "System": [
            st.Page("app_pages/model.py", title="Model", icon=":material/psychology:"),
        ],
    },
    position="sidebar",
)

uploaded = st.sidebar.file_uploader("Upload expense CSV", type=["csv"])
contamination = st.sidebar.slider(
    "Expected anomaly proportion",
    0.01,
    0.20,
    0.05,
    0.01,
    help="Isolation Forest contamination controls the expected share of unusual records.",
)

if uploaded:
    try:
        raw = pd.read_csv(uploaded)
        source_name = uploaded.name
    except Exception as error:
        st.error(f"Could not read the CSV: {error}")
        st.stop()
else:
    raw = load_default()
    source_name = "finalized_expense_transactions.csv"

missing = [column for column in REQUIRED if column not in raw.columns]
if missing:
    st.error("Dataset validation failed.")
    st.write("Missing required columns:", missing)
    st.stop()

if raw.empty:
    st.warning("The uploaded dataset is empty.")
    st.stop()

data = build_features(raw)
if data.empty:
    st.error("No valid transactions remain after preprocessing.")
    st.stop()

results, model_features = detect_anomalies(data, contamination)
anomalies = results[results["Anomaly Status"] == "Unusual"].copy()

st.session_state["expenseguard_data"] = {
    "raw": raw,
    "results": results,
    "anomalies": anomalies,
    "model_features": model_features,
    "contamination": contamination,
    "source_name": source_name,
}

st.markdown(
    f"""
<div class="hero">
<h1>ExpenseGuard AI</h1>
<p>Machine-learning anomaly detection for small-business expense transactions · Local processing · {len(results):,} validated transactions</p>
</div>
""",
    unsafe_allow_html=True,
)
st.caption(f"Data source: {Path(source_name).name}")

page.run()
