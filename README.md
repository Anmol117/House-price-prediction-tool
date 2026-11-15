# HomeValuate AI — Indian Real Estate Price Prediction Engine

Production-grade machine learning web application predicting residential property prices across major Indian metropolitan markets (**Bengaluru, Chennai, Delhi NCR, Hyderabad, Kolkata, Mumbai, Pune**). Built with **FastAPI**, **scikit-learn**, and **React 18 (TypeScript + Vite)**.

---

## Architecture Overview

```
               ┌───────────────────────┐
               │    User Browser       │
               └───────────┬───────────┘
                           │ HTTP (INR Formatting, Cascading Dropdowns)
                           ▼
               ┌───────────────────────┐
               │ React + Vite Frontend │  (Port 3000 / 5173)
               └───────────┬───────────┘
                           │ REST API (JSON)
                           ▼
               ┌───────────────────────┐
               │    FastAPI Backend    │  (Port 8000)
               └───────────┬───────────┘
                           │ Pipeline Serving
                           ▼
               ┌────────────────────────────────────────────────────────┐
               │ Scikit-Learn Pipeline (models/model.joblib)            │
               │ • OneHotEncoder (city, locality, type, furnishing)     │
               │ • ColumnTransformer (passthrough area, bhk, bathrooms) │
               │ • Random Forest Regressor (log1p price target)         │
               └────────────────────────────────────────────────────────┘
```

---

## Key Features

- **Indian Real Estate Features**:
  - `area_sqft`: Super built-up / carpet area (200 – 20,000 sq ft)
  - `bhk`: Bedrooms / BHK count (1 – 10)
  - `bathrooms`: Bathroom count (1 – 10)
  - `city`: 7 Metropolitan Hubs (Bengaluru, Chennai, Delhi NCR, Hyderabad, Kolkata, Mumbai, Pune)
  - `locality`: Cascading neighborhood dropdown (Wakad, Baner, Whitefield, Andheri West, etc.)
  - `property_type`: Apartment, Builder Floor, Independent House, Villa
  - `furnishing`: Furnished, Semi-furnished, Unfurnished
- **Empirical Prediction Intervals**: Replaces arbitrary ±10% ranges with empirical 90% prediction intervals derived from 5th and 95th percentile residual ratios on holdout test listings.
- **Indian Currency Representation**: Full support for Indian rupee formatting (`en-IN` `₹82,00,000`) and standard Indian real estate notations (`₹82.00 Lakh`, `₹1.50 Cr`).
- **3-Model ML Benchmark**: Rigorous 80/20 train/test evaluation across Linear Regression, Random Forest, and Gradient Boosting.
- **Compliance & Disclaimer**: Built-in market listing disclaimers and input sanitization against XSS/injection.

---

## Machine Learning Benchmark

Evaluated on 5,925 test listings from an 80/20 train/test split of 29,624 real Indian property records:

| Model Architecture | Test R² Score | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | Production Status |
|---|---|---|---|---|
| **Linear Regression** | 0.1502 | ₹48,17,168.01 | ₹1,30,49,671.28 | Baseline |
| **Gradient Boosting** | 0.3656 | ₹48,02,673.11 | ₹1,12,74,847.46 | Benchmark |
| **Random Forest (100 Trees)** | **0.4278** | **₹47,52,048.42** | **₹1,07,08,244.89** | **Active Production Model** |

---

## Environment Variables

| Variable | Scope | Required | Default | Description / Example |
|---|---|---|---|---|
| `MODEL_PATH` | Backend | Yes | `models/model.joblib` | Path to trained model pipeline (`.joblib`) |
| `PORT` | Backend | No | `8000` | Port for FastAPI server (1024 – 65535) |
| `CORS_ALLOWED_ORIGINS` | Backend | No | `http://localhost:3000,http://localhost:5173` | Comma-separated list of allowed origins |
| `VITE_API_URL` | Frontend | No | `http://localhost:8000` | Backend API URL used during development & build |

---

## Getting Started Locally

### Prerequisites
- **Python 3.10+** (Python 3.11 recommended)
- **Node.js 18+** & **npm 9+**

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Download and clean dataset (creates backend/data/india_housing.csv)
python prepare_dataset.py

# Train & benchmark models (creates models/model.joblib & models/model_meta.json)
python train_model.py

# Run test suite
pytest

# Start FastAPI server (runs on http://localhost:8000)
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run TypeScript build check
npm run build

# Start development server (runs on http://localhost:3000 or http://localhost:5173)
npm run dev
```

---

## API Endpoints

### 1. `POST /predict`
Predict property price based on Indian property specifications.
- **Request Body**:
  ```json
  {
    "area_sqft": 1150.0,
    "bhk": 2,
    "bathrooms": 2.0,
    "city": "Pune",
    "locality": "Wakad",
    "property_type": "Apartment",
    "furnishing": "Semi-furnished"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "predicted_price": 8173322.48,
    "price_range": {
      "lower": 3342888.89,
      "upper": 23383875.62
    },
    "currency": "INR",
    "confidence_metrics": {
      "confidence_interval": {
        "lower_bound": 3342888.89,
        "upper_bound": 23383875.62
      }
    }
  }
  ```

### 2. `GET /options`
Returns available dropdown choices (cities, cascading localities, property types, furnishing types).

### 3. `GET /model-info`
Provides model architecture, benchmark comparison table, empirical interval ratios, and dataset documentation.

### 4. `GET /health`
Verifies backend status and model loading.
- **Response (200 OK)**:
  ```json
  {
    "status": "healthy",
    "model_loaded": true
  }
  ```
