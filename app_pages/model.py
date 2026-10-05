import streamlit as st

from app_pages.common import get_workspace_data

workspace = get_workspace_data()
raw = workspace["raw"]
model_features = workspace["model_features"]
contamination = workspace["contamination"]

st.header("Detection Model")
st.caption("Understand how ExpenseGuard identifies transactions that may need a closer look.")
st.write(
    "Primary algorithm: **Isolation Forest**. The model is trained locally on the "
    "validated dataset."
)

algorithm_column, trees_column, contamination_column = st.columns(3)
algorithm_column.metric("Algorithm", "Isolation Forest")
trees_column.metric("Trees", "300")
contamination_column.metric("Contamination", f"{contamination:.0%}")

st.markdown("**Engineered features**")
st.write(", ".join(model_features))
st.markdown("**Methodology**")
st.write(
    "Numerical behavioral features are imputed and standardized before Isolation Forest. "
    "The model's decision function is inverted so that a higher displayed anomaly score "
    "corresponds to a more unusual transaction. No external API is used."
)
st.markdown("**Dataset preview**")
st.dataframe(raw.head(20), hide_index=True)
