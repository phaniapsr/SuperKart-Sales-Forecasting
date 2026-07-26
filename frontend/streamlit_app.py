"""
SuperKart Sales Forecasting — Streamlit Frontend
Loads best_model.pkl directly (no separate backend API needed).
"""

import os
import pickle
import numpy as np
import pandas as pd
import streamlit as st

# ── Load model ────────────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "best_model.pkl")

@st.cache_resource
def load_model():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

model = load_model()

# ── Constants ─────────────────────────────────────────────────────────────────
SUGAR_OPTIONS  = ["Low Fat", "Regular", "No Sugar"]
PRODUCT_TYPES  = sorted(["Meat", "Snack Foods", "Hard Drinks", "Dairy", "Canned",
                          "Soft Drinks", "Health and Hygiene", "Baking Goods", "Bread",
                          "Breakfast", "Frozen Foods", "Fruits and Vegetables",
                          "Household", "Seafood", "Starchy Foods", "Others"])
STORE_SIZES    = ["High", "Medium", "Small"]
CITY_TYPES     = ["Tier 1", "Tier 2", "Tier 3"]
STORE_TYPES    = ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"]

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SuperKart Sales Forecaster",
    page_icon="🛒",
    layout="wide",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🛒 SuperKart")
    st.markdown("**Sales Forecasting System**")
    st.markdown("---")
    st.markdown(
        "Predicts quarterly sales revenue for any  \n"
        "product–store combination using a trained  \n"
        "**XGBoost / Random Forest** model."
    )
    st.markdown("---")
    st.markdown("Built with **Streamlit**")

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🛒 SuperKart Sales Revenue Forecaster")
st.markdown(
    "Predict the sales revenue for a product at a specific SuperKart outlet.  \n"
    "Use **Single Prediction** for one record or **Batch Prediction** for a CSV file."
)

tab1, tab2 = st.tabs(["📊 Single Prediction", "📂 Batch Prediction"])

# ── TAB 1: SINGLE PREDICTION ─────────────────────────────────────────────────
with tab1:
    st.subheader("Enter Product & Store Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Product")
        product_weight = st.number_input(
            "Product Weight (kg)", min_value=0.0, max_value=50.0, value=12.5, step=0.1)
        sugar = st.selectbox("Sugar Content", SUGAR_OPTIONS)
        alloc_area = st.slider(
            "Allocated Display Area", min_value=0.0, max_value=0.25,
            value=0.10, step=0.005, format="%.3f")
        product_type = st.selectbox("Product Type", PRODUCT_TYPES,
                                    index=PRODUCT_TYPES.index("Dairy"))
        mrp = st.number_input("Product MRP (₹)", min_value=1.0, max_value=500.0,
                              value=150.0, step=1.0)

    with col2:
        st.markdown("#### Store")
        store_size = st.selectbox("Store Size", STORE_SIZES)
        city_type  = st.selectbox("City Type",  CITY_TYPES)
        store_type = st.selectbox("Store Type", STORE_TYPES)
        est_year   = st.number_input("Establishment Year",
                                     min_value=1980, max_value=2024, value=1999, step=1)
        store_age  = 2024 - est_year

    with col3:
        st.markdown("#### Summary")
        st.metric("Store Age (years)", store_age)
        st.metric("Product MRP",       f"₹ {mrp:,.0f}")
        st.metric("Display Area",      f"{alloc_area:.3f}")
        st.metric("City Tier",         city_type)

    st.markdown("---")

    if st.button("🔮  Predict Sales Revenue", type="primary"):
        input_df = pd.DataFrame([{
            "Product_Weight":            product_weight,
            "Product_Sugar_Content":     sugar,
            "Product_Allocated_Area":    alloc_area,
            "Product_Type":              product_type,
            "Product_MRP":               mrp,
            "Store_Size":                store_size,
            "Store_Location_City_Type":  city_type,
            "Store_Type":                store_type,
            "Store_Age":                 store_age,
        }])
        prediction = float(model.predict(input_df)[0])
        st.success("Prediction complete!")
        st.metric("Predicted Sales Revenue", f"₹ {prediction:,.2f}")

# ── TAB 2: BATCH PREDICTION ──────────────────────────────────────────────────
with tab2:
    st.subheader("Upload a CSV for Batch Forecasting")
    st.markdown(
        "Required columns: `Product_Weight`, `Product_Sugar_Content`, "
        "`Product_Allocated_Area`, `Product_Type`, `Product_MRP`, `Store_Size`, "
        "`Store_Location_City_Type`, `Store_Type`, `Store_Age`"
    )

    sample = pd.DataFrame([{
        "Product_Weight": 12.5, "Product_Sugar_Content": "Low Fat",
        "Product_Allocated_Area": 0.10, "Product_Type": "Dairy",
        "Product_MRP": 150.0, "Store_Size": "Medium",
        "Store_Location_City_Type": "Tier 1",
        "Store_Type": "Supermarket Type1", "Store_Age": 25,
    }, {
        "Product_Weight": 8.0, "Product_Sugar_Content": "Regular",
        "Product_Allocated_Area": 0.05, "Product_Type": "Snack Foods",
        "Product_MRP": 75.0, "Store_Size": "Small",
        "Store_Location_City_Type": "Tier 2",
        "Store_Type": "Food Mart", "Store_Age": 15,
    }])
    st.download_button("⬇️  Download Sample CSV",
                       data=sample.to_csv(index=False).encode(),
                       file_name="superkart_sample_input.csv", mime="text/csv")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded is not None:
        df_input = pd.read_csv(uploaded)
        st.write(f"**Preview** ({len(df_input)} rows):")
        st.dataframe(df_input.head(10), use_container_width=True)

        if st.button("🔮  Run Batch Forecast", type="primary"):
            preds  = model.predict(df_input)
            df_out = df_input.copy()
            df_out["Predicted_Sales_INR"] = [round(float(p), 2) for p in preds]

            st.success(f"Forecast complete for {len(preds):,} records!")
            st.dataframe(
                df_out[["Product_Type", "Product_MRP", "Store_Type",
                         "Store_Location_City_Type", "Predicted_Sales_INR"]].head(20),
                use_container_width=True,
            )

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Total Forecast",  f"₹ {sum(preds):,.2f}")
            col_b.metric("Mean per Record", f"₹ {np.mean(preds):,.2f}")
            col_c.metric("Max Prediction",  f"₹ {max(preds):,.2f}")

            st.download_button("⬇️  Download Predictions CSV",
                               data=df_out.to_csv(index=False).encode(),
                               file_name="superkart_predictions.csv", mime="text/csv")
