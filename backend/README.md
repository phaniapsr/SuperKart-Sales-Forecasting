---
title: SuperKart Sales API
emoji: 🛒
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
short_description: Flask REST API for SuperKart sales revenue forecasting
---

# SuperKart Sales Forecasting — Backend API

Flask REST API that serves predictions from the best-performing ML model
(Random Forest / XGBoost) trained on SuperKart retail sales data.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/predict` | Single prediction (JSON) |
| POST | `/batch_predict` | Batch prediction (CSV upload) |

## Single Prediction — Request Body

```json
{
  "Product_Weight": 12.5,
  "Product_Sugar_Content": "Low Fat",
  "Product_Allocated_Area": 0.10,
  "Product_Type": "Dairy",
  "Product_MRP": 150.0,
  "Store_Size": "Medium",
  "Store_Location_City_Type": "Tier 1",
  "Store_Type": "Supermarket Type1",
  "Store_Age": 25
}
```

## Frontend

👉 [superkart-sales-app](https://huggingface.co/spaces/phaniaigeek/superkart-sales-app)
