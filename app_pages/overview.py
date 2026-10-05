import pandas as pd
import plotly.express as px
import streamlit as st

from app_pages.common import get_workspace_data, money

workspace = get_workspace_data()
results = workspace["results"]
anomalies = workspace["anomalies"]

st.header("Overview")
st.caption("A high-level view of spending patterns and transactions that may need review.")

total = results["Amount"].sum()
average = results["Amount"].mean()
highest = results["Amount"].max()
count = len(anomalies)
percentage = count / len(results) * 100

columns = st.columns(5)
cards = [
    ("Total Transactions", f"{len(results):,}", "validated records"),
    ("Total Expenses", money(total), "all transactions"),
    ("Average Expense", money(average), "per transaction"),
    ("Highest Expense", money(highest), "single transaction"),
    ("Unusual Transactions", f"{count:,}", f"{percentage:.1f}% of records"),
]
for column, (label, value, note) in zip(columns, cards):
    column.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-note">{note}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="section">Spending overview</div>', unsafe_allow_html=True)
left, right = st.columns([1.45, 1])
with left:
    trend = (
        results.set_index("Date")
        .resample("ME")["Amount"]
        .sum()
        .reset_index()
    )
    figure = px.line(trend, x="Date", y="Amount", markers=True, title="Monthly expense trend")
    figure.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=55, b=10),
        yaxis_title="Expense (₹)",
        xaxis_title="",
    )
    st.plotly_chart(figure)
with right:
    categories = (
        results.groupby("Expense Category", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
    )
    figure = px.bar(
        categories,
        x="Amount",
        y="Expense Category",
        orientation="h",
        title="Category-wise spending",
    )
    figure.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=55, b=10),
        xaxis_title="Expense (₹)",
        yaxis_title="",
    )
    st.plotly_chart(figure)

left, right = st.columns(2)
with left:
    status = (
        results["Anomaly Status"]
        .value_counts()
        .rename_axis("Status")
        .reset_index(name="Transactions")
    )
    figure = px.pie(
        status,
        names="Status",
        values="Transactions",
        hole=0.58,
        title="Normal vs unusual transactions",
    )
    figure.update_layout(height=340, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(figure)
with right:
    figure = px.histogram(
        results,
        x="Anomaly Score",
        nbins=30,
        title="Anomaly score distribution",
    )
    figure.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=55, b=10),
        xaxis_title="Higher score = more unusual",
    )
    st.plotly_chart(figure)
