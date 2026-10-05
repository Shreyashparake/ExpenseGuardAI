import pandas as pd
import streamlit as st

from app_pages.common import get_workspace_data

workspace = get_workspace_data()
raw = workspace["raw"]
results = workspace["results"]
anomalies = workspace["anomalies"]

st.header("Insights")
st.caption("Compare spending concentration and review the quality of the uploaded data.")

top_categories = (
    results.groupby("Expense Category")["Amount"].sum().sort_values(ascending=False)
)
top_vendors = results.groupby("Vendor")["Amount"].sum().sort_values(ascending=False)
unusual_by_category = (
    anomalies.groupby("Expense Category")["Amount"]
    .agg(["count", "sum"])
    .sort_values("count", ascending=False)
    if len(anomalies)
    else pd.DataFrame()
)

left, right = st.columns(2)
with left:
    st.markdown("**Highest spending categories**")
    st.dataframe(
        top_categories.head(8).rename("Total Expense").to_frame(),
    )
with right:
    st.markdown("**Highest spending vendors**")
    st.dataframe(
        top_vendors.head(8).rename("Total Expense").to_frame(),
    )

if not unusual_by_category.empty:
    st.markdown("**Unusual transactions by category**")
    unusual_by_category.columns = ["Unusual Transactions", "Unusual Amount"]
    st.dataframe(unusual_by_category)

st.markdown("**Data quality summary**")
quality = pd.DataFrame(
    {
        "Check": [
            "Rows received",
            "Rows after preprocessing",
            "Duplicate transaction IDs removed",
            "Invalid/missing amount or date rows removed",
        ],
        "Result": [
            len(raw),
            len(results),
            max(0, raw["Transaction ID"].nunique() - len(results)),
            max(
                0,
                len(raw)
                - len(results)
                - max(0, raw["Transaction ID"].nunique() - len(results)),
            ),
        ],
    }
)
st.dataframe(quality, hide_index=True)
