import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Afficionado Coffee Roasters Dashboard",
    page_icon="☕",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("☕ Afficionado Coffee Roasters")
st.subheader("Sales Trend and Time-Based Performance Analysis")

st.write(
    "Interactive dashboard for analyzing revenue performance, "
    "transaction hours, time buckets, store locations and "
    "product categories."
)

# =========================================================
# LOAD EXCEL DATA
# =========================================================

FILE_NAME = "Afficionado_Coffee_Roasters_Final.xlsx"

try:
    df = pd.read_excel(
        FILE_NAME,
        sheet_name="Transactions"
    )
except Exception as e:
    st.error("Dataset could not be loaded.")
    st.error(f"Error: {e}")
    st.stop()

# =========================================================
# CLEAN COLUMN NAMES
# =========================================================

df.columns = df.columns.str.strip()

# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_columns = [
    "transaction_id",
    "transaction_qty",
    "store_location",
    "product_category",
    "product_detail",
    "hour",
    "revenue",
    "time_bucket"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error("Missing columns in Transactions sheet:")
    st.write(missing_columns)
    st.stop()

# =========================================================
# DATA TYPES
# =========================================================

df["revenue"] = pd.to_numeric(
    df["revenue"],
    errors="coerce"
)

df["transaction_qty"] = pd.to_numeric(
    df["transaction_qty"],
    errors="coerce"
)

df["hour"] = pd.to_numeric(
    df["hour"],
    errors="coerce"
)

df = df.dropna(
    subset=["revenue", "hour"]
)

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Filters")

# Store Location
stores = sorted(
    df["store_location"].dropna().unique()
)

selected_stores = st.sidebar.multiselect(
    "Store Location",
    stores,
    default=stores
)

# Time Bucket
time_buckets = list(
    df["time_bucket"].dropna().unique()
)

selected_time_buckets = st.sidebar.multiselect(
    "Time Bucket",
    time_buckets,
    default=time_buckets
)

# Product Category
categories = sorted(
    df["product_category"].dropna().unique()
)

selected_categories = st.sidebar.multiselect(
    "Product Category",
    categories,
    default=categories
)

# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df[
    (df["store_location"].isin(selected_stores))
    &
    (df["time_bucket"].isin(selected_time_buckets))
    &
    (df["product_category"].isin(selected_categories))
]

# =========================================================
# KPI SECTION
# =========================================================

st.markdown("## 📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered_df["revenue"].sum()

total_transactions = filtered_df["transaction_id"].nunique()

total_quantity = filtered_df["transaction_qty"].sum()

if total_transactions > 0:
    average_transaction = (
        total_revenue / total_transactions
    )
else:
    average_transaction = 0

col1.metric(
    "💰 Total Revenue",
    f"${total_revenue:,.2f}"
)

col2.metric(
    "🧾 Total Transactions",
    f"{total_transactions:,}"
)

col3.metric(
    "📦 Total Quantity Sold",
    f"{total_quantity:,.0f}"
)

col4.metric(
    "💵 Avg. Revenue / Transaction",
    f"${average_transaction:,.2f}"
)

# =========================================================
# REVENUE BY HOUR
# =========================================================

st.markdown("## ⏰ Revenue by Hour")

hour_revenue = (
    filtered_df
    .groupby("hour", as_index=False)["revenue"]
    .sum()
    .sort_values("hour")
)

fig_hour = px.line(
    hour_revenue,
    x="hour",
    y="revenue",
    markers=True,
    title="Revenue Trend by Hour"
)

fig_hour.update_layout(
    xaxis_title="Hour",
    yaxis_title="Revenue"
)

st.plotly_chart(
    fig_hour,
    use_container_width=True
)

# =========================================================
# PEAK HOUR
# =========================================================

if not hour_revenue.empty:

    peak_hour_row = hour_revenue.loc[
        hour_revenue["revenue"].idxmax()
    ]

    peak_hour = int(
        peak_hour_row["hour"]
    )

    peak_revenue = peak_hour_row["revenue"]

    st.success(
        f"🔥 Peak revenue hour: {peak_hour}:00 "
        f"with revenue of ${peak_revenue:,.2f}"
    )

# =========================================================
# TIME BUCKET ANALYSIS
# =========================================================

st.markdown("## 🕒 Revenue by Time Bucket")

bucket_revenue = (
    filtered_df
    .groupby("time_bucket", as_index=False)["revenue"]
    .sum()
    .sort_values(
        "revenue",
        ascending=False
    )
)

fig_bucket = px.bar(
    bucket_revenue,
    x="time_bucket",
    y="revenue",
    title="Revenue Performance by Time Bucket",
    text_auto=".2s"
)

fig_bucket.update_layout(
    xaxis_title="Time Bucket",
    yaxis_title="Revenue"
)

st.plotly_chart(
    fig_bucket,
    use_container_width=True
)

# =========================================================
# STORE LOCATION ANALYSIS
# =========================================================

st.markdown("## 📍 Store Location Performance")

store_revenue = (
    filtered_df
    .groupby(
        "store_location",
        as_index=False
    )["revenue"]
    .sum()
    .sort_values(
        "revenue",
        ascending=False
    )
)

fig_store = px.bar(
    store_revenue,
    x="store_location",
    y="revenue",
    title="Revenue by Store Location",
    text_auto=".2s"
)

fig_store.update_layout(
    xaxis_title="Store Location",
    yaxis_title="Revenue"
)

st.plotly_chart(
    fig_store,
    use_container_width=True
)

# =========================================================
# PRODUCT CATEGORY ANALYSIS
# =========================================================

st.markdown("## 🥐 Product Category Performance")

category_revenue = (
    filtered_df
    .groupby(
        "product_category",
        as_index=False
    )["revenue"]
    .sum()
    .sort_values(
        "revenue",
        ascending=False
    )
)

fig_category = px.pie(
    category_revenue,
    names="product_category",
    values="revenue",
    title="Revenue Distribution by Product Category"
)

st.plotly_chart(
    fig_category,
    use_container_width=True
)

# =========================================================
# TOP 10 PRODUCTS
# =========================================================

st.markdown("## 🏆 Top 10 Products")

top_products = (
    filtered_df
    .groupby(
        "product_detail",
        as_index=False
    )["revenue"]
    .sum()
    .sort_values(
        "revenue",
        ascending=False
    )
    .head(10)
)

fig_product = px.bar(
    top_products.sort_values("revenue"),
    x="revenue",
    y="product_detail",
    orientation="h",
    title="Top 10 Products by Revenue",
    text_auto=".2s"
)

fig_product.update_layout(
    xaxis_title="Revenue",
    yaxis_title="Product"
)

st.plotly_chart(
    fig_product,
    use_container_width=True
)

# =========================================================
# STORE × TIME BUCKET ANALYSIS
# =========================================================

st.markdown("## 📍 Store × Time Bucket Analysis")

store_bucket = (
    filtered_df
    .groupby(
        [
            "store_location",
            "time_bucket"
        ],
        as_index=False
    )["revenue"]
    .sum()
)

fig_store_bucket = px.bar(
    store_bucket,
    x="store_location",
    y="revenue",
    color="time_bucket",
    barmode="group",
    title="Revenue by Store Location and Time Bucket"
)

fig_store_bucket.update_layout(
    xaxis_title="Store Location",
    yaxis_title="Revenue"
)

st.plotly_chart(
    fig_store_bucket,
    use_container_width=True
)

# =========================================================
# TRANSACTION QUANTITY BY CATEGORY
# =========================================================

st.markdown("## 📦 Quantity Sold by Product Category")

category_quantity = (
    filtered_df
    .groupby(
        "product_category",
        as_index=False
    )["transaction_qty"]
    .sum()
    .sort_values(
        "transaction_qty",
        ascending=False
    )
)

fig_quantity = px.bar(
    category_quantity,
    x="product_category",
    y="transaction_qty",
    title="Quantity Sold by Product Category",
    text_auto=".2s"
)

fig_quantity.update_layout(
    xaxis_title="Product Category",
    yaxis_title="Quantity Sold"
)

st.plotly_chart(
    fig_quantity,
    use_container_width=True
)

# =========================================================
# TRANSACTIONS BY HOUR
# =========================================================

st.markdown("## 🧾 Transactions by Hour")

hour_transactions = (
    filtered_df
    .groupby("hour")["transaction_id"]
    .nunique()
    .reset_index(name="transactions")
    .sort_values("hour")
)

fig_transactions = px.bar(
    hour_transactions,
    x="hour",
    y="transactions",
    title="Number of Transactions by Hour",
    text_auto=".2s"
)

fig_transactions.update_layout(
    xaxis_title="Hour",
    yaxis_title="Transactions"
)

st.plotly_chart(
    fig_transactions,
    use_container_width=True
)

# =========================================================
# FILTERED TRANSACTION DATA
# =========================================================

st.markdown("## 📋 Filtered Transaction Data")

st.dataframe(
    filtered_df,
    use_container_width=True
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Afficionado Coffee Roasters | "
    "Sales Trend and Time-Based Performance Analysis"
)
