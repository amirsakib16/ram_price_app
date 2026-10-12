import os
import pickle
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load the model package
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "ram_price_model.pkl")
with open(MODEL_PATH, "rb") as f:
    model_data = pickle.load(f)

pipeline_model = model_data["model"]
preprocessor = model_data["preprocessor"]
classes = model_data["classes"]
feature_info = model_data["features"]

# Common brands for the UI (top ones + popular)
COMMON_BRANDS = sorted([
    "Kingston", "Corsair", "Samsung", "Crucial", "G.Skill", "TeamGroup",
    "Patriot", "ADATA", "Micron", "Hynix", "SK Hynix", "HP", "Dell",
    "Lexar", "PNY", "Transcend", "Silicon Power", "Unbranded", "Other"
])

@app.route("/")
def index():
    return render_template(
        "index.html",
        brands=COMMON_BRANDS,
        generations=["DDR3", "DDR4", "DDR5"],
        conditions=["New", "Open box", "Refurbished", "Used", "Parts Only"],
        unit_types=["Single", "Dual Kit", "Bulk"],
    )

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json() if request.is_json else request.form

        # Extract and validate inputs
        capacity_gb = float(data.get("capacity_gb", 0))
        bus_speed_mhz = float(data.get("bus_speed_mhz", 0))
        demand_ratio = float(data.get("demand_ratio", 1.0))
        has_discount = int(data.get("has_discount", 0))

        ram_generation = str(data.get("ram_generation", "DDR4")).strip()
        condition_clean = str(data.get("condition_clean", "Used")).strip()
        unit_type = str(data.get("unit_type", "Single")).strip()
        brand = str(data.get("brand", "Other")).strip()
        if brand == "Other":
            brand = "Unbranded"

        is_ecc = int(data.get("is_ecc", 0))
        is_sodimm = int(data.get("is_sodimm", 0))
        is_gaming = int(data.get("is_gaming", 0))
        is_us_listing = int(data.get("is_us_listing", 1))
        is_bulk_server = int(data.get("is_bulk_server", 0))

        # Build input DataFrame with exact column order expected by preprocessor
        input_df = pd.DataFrame([{
            "capacity_gb": capacity_gb,
            "bus_speed_mhz": bus_speed_mhz,
            "demand_ratio": demand_ratio,
            "has_discount": has_discount,
            "ram_generation": ram_generation,
            "condition_clean": condition_clean,
            "unit_type": unit_type,
            "brand": brand,
            "is_ecc": is_ecc,
            "is_sodimm": is_sodimm,
            "is_gaming": is_gaming,
            "is_us_listing": is_us_listing,
            "is_bulk_server": is_bulk_server,
        }])

        # Preprocess and predict
        X = preprocessor.transform(input_df)
        pred_label = pipeline_model.predict(X)[0]
        proba = pipeline_model.predict_proba(X)[0]

        # proba order matches model.classes_
        model_classes = list(getattr(pipeline_model, "classes_", classes))
        proba_dict = {str(cls): float(p) for cls, p in zip(model_classes, proba)}

        # Ensure consistent class order from package
        ordered_proba = {cls: proba_dict.get(cls, 0.0) for cls in classes}

        return jsonify({
            "success": True,
            "prediction": str(pred_label),
            "probabilities": ordered_proba,
            "classes": classes,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/health")
def health():
    return jsonify({"status": "ok", "model": model_data.get("model_name", "SVM")})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
