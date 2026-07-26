"""
SuperKart Sales Forecasting — Flask Backend API  (rubric reference)
Endpoints:
  GET  /health          → health check
  POST /predict         → single prediction (JSON body)
  POST /batch_predict   → batch prediction (CSV file upload)
"""

import os, io, pickle, logging
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", "models/best_model.pkl")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)
logger.info("Model loaded from %s", MODEL_PATH)

REQUIRED_FIELDS = [
    "Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area",
    "Product_Type", "Product_MRP", "Store_Size",
    "Store_Location_City_Type", "Store_Type", "Store_Age",
]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "model_loaded": True})


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(force=True, silent=True)
    if not payload:
        return jsonify({"error": "Request body must be valid JSON."}), 400
    missing = [f for f in REQUIRED_FIELDS if f not in payload]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400
    try:
        df   = pd.DataFrame([payload])
        pred = float(model.predict(df)[0])
        return jsonify({"predicted_sales": round(pred, 2), "currency": "INR"})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/batch_predict", methods=["POST"])
def batch_predict():
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Use multipart field 'file'."}), 400
    try:
        df    = pd.read_csv(io.StringIO(request.files["file"].read().decode("utf-8")))
        preds = model.predict(df[REQUIRED_FIELDS]).tolist()
        return jsonify({"count": len(preds), "predicted_sales": [round(p, 2) for p in preds]})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 7860)))
