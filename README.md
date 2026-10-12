# RAM Price Category Predictor

A Flask web application that predicts whether a RAM module is **Budget**, **Mid-Range**, or **Premium** using a trained SVM classifier with preprocessing pipeline.

## Features

- Clean, modern dark UI (HTML + CSS + JS)
- Flask backend with JSON API
- Handles numerical, categorical, and binary features
- Probability breakdown for each class
- Deploy-ready for [Render](https://render.com)

## Project Structure

```
ram_price_app/
├── app.py                 # Flask application
├── requirements.txt
├── Procfile               # For Render / Heroku-style hosts
├── render.yaml            # Render Blueprint
├── model/
│   └── ram_price_model.pkl
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## Local Development

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
# → http://localhost:5000
```

## Deploy to Render

### Option A – Blueprint (recommended)

1. Push this folder to a GitHub repository.
2. In Render Dashboard → **New** → **Blueprint**.
3. Connect the repo. Render will detect `render.yaml` and create the web service.

### Option B – Manual Web Service

1. Push to GitHub.
2. Render → **New** → **Web Service**.
3. Connect repo.
4. Settings:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
5. Deploy.

The free tier is sufficient for this app.

## API

### `POST /predict`

**Request body (JSON):**

```json
{
  "capacity_gb": 16,
  "bus_speed_mhz": 3200,
  "demand_ratio": 1.0,
  "has_discount": 0,
  "ram_generation": "DDR4",
  "condition_clean": "Used",
  "unit_type": "Single",
  "brand": "Kingston",
  "is_ecc": 0,
  "is_sodimm": 0,
  "is_gaming": 0,
  "is_us_listing": 1,
  "is_bulk_server": 0
}
```

**Response:**

```json
{
  "success": true,
  "prediction": "Mid-Range",
  "probabilities": {
    "Budget": 0.12,
    "Mid-Range": 0.71,
    "Premium": 0.17
  },
  "classes": ["Budget", "Mid-Range", "Premium"]
}
```

### `GET /health`

Returns `{"status": "ok", "model": "SVM"}`.

## Model Notes

- Classifier: SVM (`SVC` with `probability=True`)
- Preprocessing: median/most-frequent imputation, standard scaling, one-hot encoding
- Input features are defined in the pickled package under `features`
- Model was trained with scikit-learn 1.6.1 — keep that version in production for compatibility
