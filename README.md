# House Price Prediction Website (HomeValuate AI)

Full-stack machine learning web application for estimating residential property prices using a trained Linear Regression model. Built with **FastAPI**, **scikit-learn**, and **React 18 (TypeScript + Vite)**.

---

## Architecture Overview

```
               ┌───────────────────────┐
               │    User Browser       │
               └───────────┬───────────┘
                           │ HTTP
                           ▼
               ┌───────────────────────┐
               │ React + Vite Frontend │  (Port 3000)
               └───────────┬───────────┘
                           │ REST API (JSON)
                           ▼
               ┌───────────────────────┐
               │    FastAPI Backend    │  (Port 8000)
               └───────────┬───────────┘
                           │ In-Memory Serving
                           ▼
               ┌───────────────────────┐
               │ Scikit-Learn Model    │  (model.pkl)
               └───────────────────────┘
```

---

## Features

- **Instant Valuation Engine**: Real-time price estimation from square footage, bedrooms, bathrooms, location, and year built.
- **Statistical Confidence Intervals**: Returns lower and upper confidence bounds (90% interval).
- **Client-Side & Server-Side Validation**:
  - `square_footage`: 1 – 100,000 sq ft
  - `bedrooms`: 0 – 20
  - `bathrooms`: 0 – 20 (0.5 increments)
  - `location`: Alphanumeric with standard punctuation (max 200 chars), with automatic regex sanitization
  - `year_built`: 1800 to current year + 1
- **Model Transparency & Architecture Page**: Dedicated `/about` route presenting feature definitions, data pipeline, RMSE, and R² metrics.
- **Production Ready**: 1 MB payload limits, CORS middleware, standardized `{"error": ...}` responses, Dockerfiles, and compose orchestrator.

---

## Environment Variables

| Variable | Scope | Required | Default | Description / Example |
|---|---|---|---|---|
| `MODEL_PATH` | Backend | Yes | `models/model.pkl` | Path to trained model file (`.pkl` or `.joblib`) |
| `PORT` | Backend | No | `8000` | Port for FastAPI server (1024 – 65535) |
| `CORS_ALLOWED_ORIGINS` | Backend | No | `http://localhost:3000` | Comma-separated list of allowed origins |
| `VITE_API_URL` | Frontend | No | `http://localhost:8000` | Backend API URL used during development & build |
| `REACT_APP_API_URL` | Frontend | No | `http://localhost:8000` | Alternative build-time API URL |

---

## Getting Started Locally

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm 9+**

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate   # On Windows
# source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Train baseline model (if not already trained)
python train_model.py

# Run tests
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

# Start Vite development server (runs on http://localhost:3000)
npm run dev
```

---

## Running with Docker

You can run both services simultaneously using Docker Compose:

```bash
# Build and start all containers
docker-compose up --build

# Open the application
# Frontend: http://localhost:3000
# Backend API Docs: http://localhost:8000/docs
```

To stop the services:
```bash
docker-compose down
```

---

## API Endpoints

### 1. `POST /predict`
Predict property price based on specifications.
- **Request Body**:
  ```json
  {
    "square_footage": 2400.0,
    "bedrooms": 3,
    "bathrooms": 2.5,
    "location": "Austin, TX",
    "year_built": 2018
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "predicted_price": 704818.25,
    "confidence_metrics": {
      "confidence_interval": {
        "lower_bound": 634336.43,
        "upper_bound": 775300.08
      }
    }
  }
  ```
- **Error Response (400 Bad Request)**:
  ```json
  {
    "error": "Validation error: square_footage: Input should be less than or equal to 100000"
  }
  ```

### 2. `GET /health`
Verifies backend status and model loading.
- **Response (200 OK)**:
  ```json
  {
    "status": "healthy",
    "model_loaded": true
  }
  ```

### 3. `GET /model-info`
Provides model architecture, feature documentation, and evaluation statistics.
