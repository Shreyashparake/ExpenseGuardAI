# ExpenseGuard AI — Small Business Expense Anomaly Detection

Streamlit application for local small-business expense anomaly detection.

## Workspaces

Use the sidebar to move between the **Overview**, **Transactions**, **Anomaly
Review**, **Insights**, and **Detection Model** workspaces. The dataset upload
and expected anomaly proportion controls stay available while navigating.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The application uses the included finalized CSV by default. A user can also upload another CSV with the required columns.

## Required columns

- Transaction ID
- Date
- Expense Category
- Vendor
- Amount
- Payment Method
- Description
- Department/Business Unit

## ML

Isolation Forest is used as the primary unsupervised anomaly detector. Processing is local; there are no third-party APIs.

Anomaly means a transaction requiring review, not automatically fraud or an incorrect transaction.
