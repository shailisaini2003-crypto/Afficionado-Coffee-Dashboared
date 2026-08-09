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
    "Interactive dashboard for analyzing sales performance, "
    "peak transaction hours, time buckets, store locations "
    "and product categories."
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
    st.error(f"Actual error: {e}")
    st.stop()

# =========================================================
# CLEAN COLUMN NAMES
# =========================================================

df.columns = df.columns.astype(str).str.strip()

# =========================================================
# CHECK REQUIRED COLUMNS
# =========================================================

required_columns = [
    "transaction_id",
    "transaction_qty",
    "store_location",
    "product_category",
    "product_detail",
    "revenue",
    "hour",
    "time_bucket"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error("Required columns are missing from Transactions sheet:")
    st.write(missing_columns)
    st.write("Available columns:")
    st.write(list(df.columns))
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
# USER-FRIENDLY COLUMN NAMES
# =========================================================

df["Sales"] = df["revenue"]
df["Hour"] = df["hour"]
df["Time Slot"] = df["time_bucket"]

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Filters")

# Store filter
stores = sorted(
    df["store_location"]
    .dropna()
    .unique()
)

selected_stores = st.sidebar.multiselect(
    "Store Location",
    stores,
    default=stores
)

# Time bucket filter
time_slots = sorted(
    df["Time Slot"]
    .dropna()
    .unique()
)

selected_time_slots = st.sidebar.multiselect(
    "Time Bucket",
    time_slots,
    default=time_slots
)

# Product category filter
categories = sorted(
    df["product_category"]
    .dropna()
    .unique()
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
    (df["Time Slot"].isin(selected_time_slots))
    &
    (df["product_category"].isin(selected_categories))
]

# =========================================================
# KPI SECTION
# =========================================================

st.markdown("## 📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

total_sales = filtered_df["Sales"].sum()

total_transactions = (
    filtered_df["transaction_id"].nunique()
)

total_quantity = (
    filtered_df["transaction_qty"].sum()
)

if total_transactions > 0:
    average_transaction = (
        total_sales / total_transactions
    )
else:
    average_transaction = 0

col1.metric(
    "💰 Total Revenue",
    f"${total_sales:,.2f}"
)

col2.metric(
    "🧾 Total Transactions",
    f"{total_transactions:,}"
)

col3.metric(
    "📦 Total Quantity",
    f"{total_quantity:,.0f}"
)

col4.metric(
    "💵 Avg. Revenue / Transaction",
    f"${average_transaction:,.2f}"
)

# =========================================================
# HOURLY ANALYSIS
# =========================================================

st.markdown("## ⏰ Hourly Analysis")

hour_sales = (
    filtered_df
    .groupby("Hour", as_index=False)["Sales"]
    .sum()
    .sort_values("Hour")
)

fig_hour = px.line(
    hour_sales,
    x="Hour",
    y="Sales",
    markers=True,
    title="Sales Trend by Hour"
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

if not hour_sales.empty:

    peak_hour_row = hour_sales.loc[
        hour_sales["Sales"].idxmax()
    ]

    lowest_hour_row = hour_sales.loc[
        hour_sales["Sales"].idxmin()
    ]

    peak_hour = int(
        peak_hour_row["Hour"]
    )

    peak_sales = peak_hour_row["Sales"]

    lowest_hour = int(
        lowest_hour_row["Hour"]
    )

    lowest_sales = lowest_hour_row["Sales"]

    col1, col2 = st.columns(2)

    col1.success(
        f"🔥 Peak Sales Hour: {peak_hour}:00 "
        f"(${peak_sales:,.2f})"
    )

    col2.info(
        f"📉 Lowest Sales Hour: {lowest_hour}:00 "
        f"(${lowest_sales:,.2f})"
    )

# =========================================================
# TIME BUCKET ANALYSIS
# =========================================================

st.markdown("## 🕒 Time Bucket Analysis")

bucket_sales = (
    filtered_df
    .groupby("Time Slot", as_index=False)
    .agg(
        Revenue=("Sales", "sum"),
        Transactions=("transaction_id", "nunique"),
        Quantity=("transaction_qty", "sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
)

fig_bucket = px.bar(
    bucket_sales,
    x="Time Slot",
    y="Revenue",
    text_auto=".2s",
    title="Revenue by Time Bucket"
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
# STORE ANALYSIS
# =========================================================

st.markdown("## 📍 Store Analysis")

store_sales = (
    filtered_df
    .groupby("store_location", as_index=False)
    .agg(
        Revenue=("Sales", "sum"),
        Transactions=("transaction_id", "nunique"),
        Quantity=("transaction_qty", "sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
)

fig_store = px.bar(
    store_sales,
    x="store_location",
    y="Revenue",
    text_auto=".2s",
    title="Revenue by Store Location"
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
# CATEGORY ANALYSIS
# =========================================================

st.markdown("## 🥐 Category Analysis")

category_sales = (
    filtered_df
    .groupby("product_category", as_index=False)
    .agg(
        Revenue=("Sales", "sum"),
        Transactions=("transaction_id", "nunique"),
        Quantity=("transaction_qty", "sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
)

fig_category = px.bar(
    category_sales,
    x="product_category",
    y="Revenue",
    text_auto=".2s",
    title="Revenue by Product Category"
)

fig_category.update_layout(
    xaxis_title="Product Category",
    yaxis_title="Revenue"
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
    .groupby("product_detail", as_index=False)
    .agg(
        Revenue=("Sales", "sum"),
        Quantity=("transaction_qty", "sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
    .head(10)
)

fig_product = px.bar(
    top_products.sort_values("Revenue"),
    x="Revenue",
    y="product_detail",
    orientation="h",
    text_auto=".2s",
    title="Top 10 Products by Revenue"
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
# STORE × HOUR ANALYSIS
# =========================================================

st.markdown("## 📍 Store × Hour Analysis")

store_hour = (
    filtered_df
    .groupby(
        ["store_location", "Hour"],
        as_index=False
    )["Sales"]
    .sum()
)

fig_store_hour = px.bar(
    store_hour,
    x="Hour",
    y="Sales",
    color="store_location",
    barmode="group",
    title="Revenue by Store and Hour"
)

fig_store_hour.update_layout(
    xaxis_title="Hour",
    yaxis_title="Revenue"
)

st.plotly_chart(
    fig_store_hour,
    use_container_width=True
)

# =========================================================
# STORE × TIME BUCKET
# =========================================================

st.markdown("## 📍 Store × Time Bucket Analysis")

store_bucket = (
    filtered_df
    .groupby(
        ["store_location", "Time Slot"],
        as_index=False
    )["Sales"]
    .sum()
)

fig_store_bucket = px.bar(
    store_bucket,
    x="store_location",
    y="Sales",
    color="Time Slot",
    barmode="group",
    title="Revenue by Store and Time Bucket"
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
# SUMMARY TABLE
# =========================================================

st.markdown("## 📋 Store Performance Summary")

summary = (
    filtered_df
    .groupby("store_location", as_index=False)
    .agg(
        Revenue=("Sales", "sum"),
        Transactions=("transaction_id", "nunique"),
        Quantity=("transaction_qty", "sum")
    )
)

summary["Avg Revenue / Transaction"] = (
    summary["Revenue"] /
    summary["Transactions"]
)

st.dataframe(
    summary,
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
