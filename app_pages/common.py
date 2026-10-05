from pathlib import Path

import numpy as np
import pandas as pd
import sklearn.preprocessing
import streamlit as st
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

REQUIRED = [
    "Transaction ID",
    "Date",
    "Expense Category",
    "Vendor",
    "Amount",
    "Payment Method",
    "Description",
    "Department/Business Unit",
]


def money(value: float) -> str:
    return f"₹{value:,.0f}"


def render_styles() -> None:
    st.markdown(
        """
<style>
:root { --ink:#172033; --muted:#667085; --line:#e8ebf0; --soft:#f6f8fb; }
.block-container {padding-top:1.2rem; padding-bottom:2rem; max-width:1450px;}
[data-testid="stSidebar"] {border-right:1px solid #e8ebf0;}
.hero {padding:26px 30px; border:1px solid #e7eaf0; border-radius:22px;
       background:linear-gradient(135deg,#f8fbff 0%,#eef5ff 55%,#f8f7ff 100%);
       margin-bottom:20px;}
.hero h1 {font-size:34px; margin:0; color:#172033; letter-spacing:-1px;}
.hero p {margin:8px 0 0; color:#667085; font-size:15px;}
.kpi {border:1px solid #e8ebf0; border-radius:17px; padding:18px 19px; background:white;
      box-shadow:0 2px 12px rgba(16,24,40,.04); min-height:116px;}
.kpi-label {color:#667085;font-size:13px;font-weight:600;}
.kpi-value {color:#172033;font-size:28px;font-weight:750;margin-top:7px;}
.kpi-note {color:#98a2b3;font-size:12px;margin-top:4px;}
.section {font-size:21px;font-weight:750;color:#172033;margin:22px 0 10px;}
.badge-normal {background:#ecfdf3;color:#027a48;border-radius:20px;padding:4px 9px;font-weight:700;}
.badge-anomaly {background:#fff1f3;color:#c01048;border-radius:20px;padding:4px 9px;font-weight:700;}
div[data-testid="stMetric"] {border:1px solid #e8ebf0;padding:14px;border-radius:15px;background:white;}
.stButton>button {border-radius:10px;}
</style>
""",
        unsafe_allow_html=True,
    )


def build_features(data: pd.DataFrame) -> pd.DataFrame:
    d = data.copy()
    d["Date"] = pd.to_datetime(d["Date"], errors="coerce")
    d["Amount"] = pd.to_numeric(d["Amount"], errors="coerce")
    d = d.drop_duplicates(subset=["Transaction ID"], keep="first")
    d = d[d["Amount"].notna() & (d["Amount"] >= 0) & d["Date"].notna()].copy()

    d["Day"] = d["Date"].dt.day
    d["Month"] = d["Date"].dt.month
    d["Day of Week"] = d["Date"].dt.dayofweek
    d["Vendor Frequency"] = d.groupby("Vendor")["Transaction ID"].transform("count")
    d["Vendor Avg Spend"] = d.groupby("Vendor")["Amount"].transform("mean")
    d["Category Avg Spend"] = d.groupby("Expense Category")["Amount"].transform("mean")
    d["Category Deviation"] = (d["Amount"] - d["Category Avg Spend"]).abs()
    d["Relative Amount"] = (
        d["Amount"] / d["Category Avg Spend"].replace(0, np.nan)
    )
    d["Relative Amount"] = (
        d["Relative Amount"].replace([np.inf, -np.inf], np.nan).fillna(1)
    )
    d["Month Frequency"] = d.groupby(d["Date"].dt.to_period("M"))[
        "Transaction ID"
    ].transform("count")
    return d


@st.cache_data(show_spinner=False)
def detect_anomalies(
    data: pd.DataFrame, contamination: float
) -> tuple[pd.DataFrame, list[str]]:
    features = [
        "Amount",
        "Day",
        "Month",
        "Day of Week",
        "Vendor Frequency",
        "Vendor Avg Spend",
        "Category Avg Spend",
        "Category Deviation",
        "Relative Amount",
        "Month Frequency",
    ]
    x = data[features].copy()
    prep = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", sklearn.preprocessing.StandardScaler()),
        ]
    )
    transformed = prep.fit_transform(x)
    model = IsolationForest(
        n_estimators=300,
        contamination=contamination,
        random_state=42,
        n_jobs=-1,
    )
    prediction = model.fit_predict(transformed)
    raw_score = model.decision_function(transformed)
    results = data.copy()
    results["Anomaly Score"] = -raw_score
    results["Anomaly Status"] = np.where(prediction == -1, "Unusual", "Normal")
    return results, features


@st.cache_data(show_spinner=False)
def load_default() -> pd.DataFrame:
    path = Path(__file__).parent.parent / "data" / "finalized_expense_transactions.csv"
    return pd.read_csv(path)


def get_workspace_data() -> dict:
    return st.session_state["expenseguard_data"]
