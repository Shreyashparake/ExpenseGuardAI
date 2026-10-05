import streamlit as st

from app_pages.common import get_workspace_data, money

workspace = get_workspace_data()
results = workspace["results"]
anomalies = workspace["anomalies"]

st.header("Anomaly Review")
st.caption("Prioritize unusual transactions for human review; a flag is not proof of fraud.")
st.info(
    "An unusual transaction is a transaction requiring review; it is not automatically "
    "fraud or an incorrect transaction."
)

if anomalies.empty:
    st.success("No unusual transactions detected with the current contamination setting.")
else:
    display_columns = [
        "Transaction ID",
        "Date",
        "Amount",
        "Expense Category",
        "Vendor",
        "Payment Method",
        "Anomaly Score",
        "Anomaly Status",
    ]
    show = anomalies[display_columns].sort_values(
        "Anomaly Score", ascending=False
    )
    st.dataframe(show, hide_index=True)
    st.download_button(
        "Download anomaly results",
        show.to_csv(index=False).encode("utf-8"),
        "anomaly_results.csv",
        "text/csv",
    )

    st.markdown('<div class="section">Investigate a transaction</div>', unsafe_allow_html=True)
    selected = st.selectbox("Transaction ID", show["Transaction ID"].tolist())
    transaction = anomalies[anomalies["Transaction ID"] == selected].iloc[0]
    amount_column, score_column, category_column = st.columns(3)
    amount_column.metric("Amount", money(transaction["Amount"]))
    score_column.metric("Anomaly score", f'{transaction["Anomaly Score"]:.4f}')
    category_column.metric("Category", transaction["Expense Category"])

    st.markdown("**Investigation indicators**")
    indicators = []
    if transaction["Relative Amount"] >= 2:
        indicators.append(
            "Amount is substantially above the category's typical transaction level."
        )
    if transaction["Category Deviation"] > transaction["Category Avg Spend"]:
        indicators.append("Amount deviates materially from the category average.")
    if transaction["Vendor Frequency"] <= 2:
        indicators.append(
            "Vendor has relatively low transaction frequency in the dataset."
        )
    if not indicators:
        indicators.append(
            "The transaction's combined behavioral features differ from the learned "
            "normal spending pattern."
        )
    for indicator in indicators:
        st.write("• " + indicator)
    st.caption(
        "These indicators support investigation and should not be interpreted as proof of fraud."
    )
