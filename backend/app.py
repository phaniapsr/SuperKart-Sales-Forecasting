"""
SuperKart Sales Forecasting — Gradio Backend  (deployed on HF Spaces free tier)
Exposes /api/predict and /api/batch_predict automatically via Gradio.
Flask equivalent: flask_app.py
"""

import pickle
import pandas as pd
import gradio as gr

with open("models/best_model.pkl", "rb") as f:
    model = pickle.load(f)

SUGAR   = ["Low Fat", "Regular", "No Sugar"]
TYPES   = sorted(["Meat","Snack Foods","Hard Drinks","Dairy","Canned","Soft Drinks",
                  "Health and Hygiene","Baking Goods","Bread","Breakfast","Frozen Foods",
                  "Fruits and Vegetables","Household","Seafood","Starchy Foods","Others"])
SIZES   = ["High", "Medium", "Small"]
CITIES  = ["Tier 1", "Tier 2", "Tier 3"]
STORES  = ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"]


def predict(product_weight, sugar, alloc_area, product_type,
            mrp, store_size, city, store_type, store_age):
    df = pd.DataFrame([{
        "Product_Weight":            product_weight,
        "Product_Sugar_Content":     sugar,
        "Product_Allocated_Area":    alloc_area,
        "Product_Type":              product_type,
        "Product_MRP":               mrp,
        "Store_Size":                store_size,
        "Store_Location_City_Type":  city,
        "Store_Type":                store_type,
        "Store_Age":                 store_age,
    }])
    return round(float(model.predict(df)[0]), 2)


def batch_predict(file):
    df    = pd.read_csv(file)
    preds = model.predict(df)
    df["Predicted_Sales_INR"] = [round(float(p), 2) for p in preds]
    out = "/tmp/predictions.csv"
    df.to_csv(out, index=False)
    return out


single_ui = gr.Interface(
    fn=predict,
    inputs=[
        gr.Number(value=12.5,  label="Product Weight (kg)"),
        gr.Dropdown(SUGAR,     label="Sugar Content",  value="Low Fat"),
        gr.Slider(0.0, 0.25, step=0.005, value=0.10, label="Allocated Display Area"),
        gr.Dropdown(TYPES,     label="Product Type",   value="Dairy"),
        gr.Number(value=150.0, label="Product MRP (₹)"),
        gr.Dropdown(SIZES,     label="Store Size",     value="Medium"),
        gr.Dropdown(CITIES,    label="City Type",      value="Tier 1"),
        gr.Dropdown(STORES,    label="Store Type",     value="Supermarket Type1"),
        gr.Number(value=25,    label="Store Age (years)"),
    ],
    outputs=gr.Number(label="Predicted Sales Revenue (₹)"),
    title="SuperKart — Single Prediction",
    api_name="predict",
)

batch_ui = gr.Interface(
    fn=batch_predict,
    inputs=gr.File(label="Upload CSV"),
    outputs=gr.File(label="Download Predictions CSV"),
    title="SuperKart — Batch Prediction",
    api_name="batch_predict",
)

gr.TabbedInterface(
    [single_ui, batch_ui],
    ["Single Predict", "Batch Predict"],
    title="SuperKart Sales Forecasting API",
).launch()
