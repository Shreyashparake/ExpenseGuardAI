import streamlit as st

from app_pages.common import REQUIRED, get_workspace_data

workspace = get_workspace_data()
results = workspace["results"]

st.header("Transactions")
st.caption("Filter, explore, and export the validated transaction dataset.")

category_column, vendor_column, status_column, amount_column = st.columns(4)
categories = sorted(results["Expense Category"].dropna().unique())
vendors = sorted(results["Vendor"].dropna().unique())
selected_categories = category_column.multiselect("Category", categories)
selected_vendors = vendor_column.multiselect("Vendor", vendors)
selected_statuses = status_column.multiselect(
    "Status", ["Normal", "Unusual"], default=["Normal", "Unusual"]
)
amount_max = float(results["Amount"].max())
amount_range = amount_column.slider(
    "Amount range", 0.0, amount_max, (0.0, amount_max)
)

date_min = results["Date"].min().date()
date_max = results["Date"].max().date()
dates = st.date_input(
    "Date range",
    (date_min, date_max),
    min_value=date_min,
    max_value=date_max,
)

filtered = results.copy()
if selected_categories:
    filtered = filtered[filtered["Expense Category"].isin(selected_categories)]
if selected_vendors:
    filtered = filtered[filtered["Vendor"].isin(selected_vendors)]
if selected_statuses:
    filtered = filtered[filtered["Anomaly Status"].isin(selected_statuses)]
if len(dates) == 2:
    filtered = filtered[filtered["Date"].dt.date.between(dates[0], dates[1])]
filtered = filtered[filtered["Amount"].between(amount_range[0], amount_range[1])]

display_columns = REQUIRED + ["Anomaly Score", "Anomaly Status"]
st.caption(f"Showing **{len(filtered):,}** of **{len(results):,}** transactions")
st.dataframe(
    filtered[display_columns].sort_values("Anomaly Score", ascending=False),
    hide_index=True,
)
st.download_button(
    "Download filtered transactions",
    filtered[display_columns].to_csv(index=False).encode("utf-8"),
    "filtered_transactions.csv",
    "text/csv",
)
