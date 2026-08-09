import streamlit as st
import pandas as pd
import plotly.express as px


# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------

st.set_page_config(
    page_title="Afficionado Coffee Roasters Dashboard",
    page_icon="☕",
    layout="wide"
)


# -------------------------------------------------
# TITLE
# -------------------------------------------------

st.title("☕ Afficionado Coffee Roasters")
st.subheader("Sales Trend and Time-Based Performance Analysis")

st.write(
    "Interactive dashboard for analyzing sales performance, "
    "peak transaction hours, time slots, store locations "
    "and product categories."
)


# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

FILE_NAME = "Afficionado_Coffee_Roasters_Final.xslx"

try:
    df = pd.read_excel(
        FILE_NAME,
        sheet_name="Transactions"
    )
except Exception as e:
    st.error("Dataset could not be loaded.")
    st.write(
        "Make sure the Excel file is uploaded in the same "
        "GitHub repository."
    )
    st.stop()


# -------------------------------------------------
# CLEAN COLUMN NAMES
# -------------------------------------------------

df.columns = df.columns.str.strip()


# -------------------------------------------------
# REQUIRED COLUMNS
# -------------------------------------------------

required_columns = [
    "transaction_id",
    "transaction_qty",
    "store_location",
    "product_category",
    "product_detail",
    "Sales",
    "Hour",
    "Time Slot"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error("Missing columns in dataset:")
    st.write(missing_columns)
    st.stop()


# -------------------------------------------------
# DATA TYPES
# -------------------------------------------------

df["Sales"] = pd.to_numeric(
    df["Sales"],
    errors="coerce"
)

df["transaction_qty"] = pd.to_numeric(
    df["transaction_qty"],
    errors="coerce"
)

df["Hour"] = pd.to_numeric(
    df["Hour"],
    errors="coerce"
)

df = df.dropna(
    subset=["Sales", "Hour"]
)


# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------

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


# Time Slot
time_slots = sorted(
    df["Time Slot"].dropna().unique()
)

selected_time_slots = st.sidebar.multiselect(
    "Time Slot",
    time_slots,
    default=time_slots
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


# -------------------------------------------------
# APPLY FILTERS
# -------------------------------------------------

filtered_df = df[
    (df["store_location"].isin(selected_stores))
    &
    (df["Time Slot"].isin(selected_time_slots))
    &
    (df["product_category"].isin(selected_categories))
]


# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------

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
    "💰 Total Sales",
    f"${total_sales:,.2f}"
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
    "💵 Avg. Transaction Value",
    f"${average_transaction:,.2f}"
)


# -------------------------------------------------
# SALES BY HOUR
# -------------------------------------------------

st.markdown("## ⏰ Sales by Hour")

hour_sales = (
    filtered_df
    .groupby(
        "Hour",
        as_index=False
    )["Sales"]
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
    yaxis_title="Sales"
)

st.plotly_chart(
    fig_hour,
    use_container_width=True
)


# -------------------------------------------------
# PEAK HOUR
# -------------------------------------------------

if not hour_sales.empty:

    peak_hour_row = hour_sales.loc[
        hour_sales["Sales"].idxmax()
    ]

    peak_hour = int(
        peak_hour_row["Hour"]
    )

    peak_sales = peak_hour_row["Sales"]

    st.success(
        f"🔥 Peak sales hour: {peak_hour}:00 "
        f"with sales of ${peak_sales:,.2f}"
    )


# -------------------------------------------------
# TIME SLOT ANALYSIS
# -------------------------------------------------

st.markdown("## 🕒 Sales by Time Slot")

slot_sales = (
    filtered_df
    .groupby(
        "Time Slot",
        as_index=False
    )["Sales"]
    .sum()
    .sort_values(
        "Sales",
        ascending=False
    )
)


fig_slot = px.bar(
    slot_sales,
    x="Time Slot",
    y="Sales",
    title="Sales Performance by Time Slot",
    text_auto=".2s"
)

fig_slot.update_layout(
    xaxis_title="Time Slot",
    yaxis_title="Sales"
)

st.plotly_chart(
    fig_slot,
    use_container_width=True
)


# -------------------------------------------------
# STORE LOCATION ANALYSIS
# -------------------------------------------------

st.markdown("## 📍 Store Location Performance")

store_sales = (
    filtered_df
    .groupby(
        "store_location",
        as_index=False
    )["Sales"]
    .sum()
    .sort_values(
        "Sales",
        ascending=False
    )
)


fig_store = px.bar(
    store_sales,
    x="store_location",
    y="Sales",
    title="Sales by Store Location",
    text_auto=".2s"
)

fig_store.update_layout(
    xaxis_title="Store Location",
    yaxis_title="Sales"
)

st.plotly_chart(
    fig_store,
    use_container_width=True
)


# -------------------------------------------------
# PRODUCT CATEGORY ANALYSIS
# -------------------------------------------------

st.markdown("## 🥐 Product Category Performance")

category_sales = (
    filtered_df
    .groupby(
        "product_category",
        as_index=False
    )["Sales"]
    .sum()
    .sort_values(
        "Sales",
        ascending=False
    )
)


fig_category = px.pie(
    category_sales,
    names="product_category",
    values="Sales",
    title="Sales Distribution by Product Category"
)

st.plotly_chart(
    fig_category,
    use_container_width=True
)


# -------------------------------------------------
# TOP 10 PRODUCTS
# -------------------------------------------------

st.markdown("## 🏆 Top 10 Products")

top_products = (
    filtered_df
    .groupby(
        "product_detail",
        as_index=False
    )["Sales"]
    .sum()
    .sort_values(
        "Sales",
        ascending=False
    )
    .head(10)
)


fig_product = px.bar(
    top_products.sort_values("Sales"),
    x="Sales",
    y="product_detail",
    orientation="h",
    title="Top 10 Products by Sales",
    text_auto=".2s"
)

fig_product.update_layout(
    xaxis_title="Sales",
    yaxis_title="Product"
)

st.plotly_chart(
    fig_product,
    use_container_width=True
)


# -------------------------------------------------
# STORE + TIME SLOT ANALYSIS
# -------------------------------------------------

st.markdown("## 📍 Store vs Time Slot")

store_slot = (
    filtered_df
    .groupby(
        [
            "store_location",
            "Time Slot"
        ],
        as_index=False
    )["Sales"]
    .sum()
)


fig_store_slot = px.bar(
    store_slot,
    x="store_location",
    y="Sales",
    color="Time Slot",
    barmode="group",
    title="Sales by Store Location and Time Slot"
)

st.plotly_chart(
    fig_store_slot,
    use_container_width=True
)


# -------------------------------------------------
# FILTERED DATA TABLE
# -------------------------------------------------

st.markdown("## 📋 Filtered Transaction Data")

st.dataframe(
    filtered_df,
    use_container_width=True
)


# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.markdown("---")

st.caption(
    "Afficionado Coffee Roasters | "
    "Sales Trend and Time-Based Performance Analysis"
)
