"""
SuperKart Sales Forecasting — Gradio Frontend  (deployed on HF Spaces free tier)
Calls the backend Space API via gradio_client.
Streamlit equivalent: streamlit_app.py
"""

import gradio as gr
from gradio_client import Client

BACKEND_SPACE = "phaniaigeek/superkart-sales-api"

SUGAR   = ["Low Fat", "Regular", "No Sugar"]
TYPES   = sorted(["Meat","Snack Foods","Hard Drinks","Dairy","Canned","Soft Drinks",
                  "Health and Hygiene","Baking Goods","Bread","Breakfast","Frozen Foods",
                  "Fruits and Vegetables","Household","Seafood","Starchy Foods","Others"])
SIZES   = ["High", "Medium", "Small"]
CITIES  = ["Tier 1", "Tier 2", "Tier 3"]
STORES  = ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"]


def predict(product_weight, sugar, alloc_area, product_type,
            mrp, store_size, city, store_type, store_age):
    try:
        client = Client(BACKEND_SPACE)
        result = client.predict(
            product_weight, sugar, alloc_area, product_type,
            mrp, store_size, city, store_type, store_age,
            api_name="/predict",
        )
        return f"₹ {float(result):,.2f}"
    except Exception as e:
        return f"Error: {e}"


def batch_predict(file):
    try:
        client = Client(BACKEND_SPACE)
        result = client.predict(file, api_name="/batch_predict")
        return result
    except Exception as e:
        return None


with gr.Blocks(title="SuperKart Sales Forecaster") as demo:
    gr.Markdown("# 🛒 SuperKart Sales Revenue Forecaster")
    gr.Markdown(
        "Predict quarterly sales revenue for any product–store combination.  \n"
        f"Powered by **[superkart-sales-api]"
        f"(https://huggingface.co/spaces/{BACKEND_SPACE})**"
    )

    with gr.Tabs():
        # ── Single Prediction ─────────────────────────────────────────────────
        with gr.Tab("📊 Single Prediction"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Product Details")
                    pw    = gr.Number(value=12.5,  label="Product Weight (kg)")
                    sugar = gr.Dropdown(SUGAR,     label="Sugar Content",  value="Low Fat")
                    area  = gr.Slider(0.0, 0.25, step=0.005, value=0.10,
                                      label="Allocated Display Area")
                    ptype = gr.Dropdown(TYPES,     label="Product Type",   value="Dairy")
                    mrp   = gr.Number(value=150.0, label="Product MRP (₹)")

                with gr.Column():
                    gr.Markdown("#### Store Details")
                    size  = gr.Dropdown(SIZES,  label="Store Size",  value="Medium")
                    city  = gr.Dropdown(CITIES, label="City Type",   value="Tier 1")
                    stype = gr.Dropdown(STORES, label="Store Type",  value="Supermarket Type1")
                    age   = gr.Number(value=25,  label="Store Age (years)")

            predict_btn = gr.Button("🔮 Predict Sales Revenue", variant="primary")
            output_box  = gr.Textbox(label="Predicted Sales Revenue", interactive=False)

            predict_btn.click(
                fn=predict,
                inputs=[pw, sugar, area, ptype, mrp, size, city, stype, age],
                outputs=output_box,
            )

        # ── Batch Prediction ──────────────────────────────────────────────────
        with gr.Tab("📂 Batch Prediction"):
            gr.Markdown(
                "Upload a CSV with columns: `Product_Weight`, `Product_Sugar_Content`, "
                "`Product_Allocated_Area`, `Product_Type`, `Product_MRP`, `Store_Size`, "
                "`Store_Location_City_Type`, `Store_Type`, `Store_Age`"
            )
            file_input  = gr.File(label="Upload CSV")
            batch_btn   = gr.Button("🔮 Run Batch Forecast", variant="primary")
            file_output = gr.File(label="Download Predictions CSV")

            batch_btn.click(fn=batch_predict, inputs=file_input, outputs=file_output)

demo.launch()
