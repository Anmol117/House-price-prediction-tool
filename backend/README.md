# House Price Prediction API - Backend

## Overview

This is the backend component of the House Price Prediction web application. It provides a REST API built with FastAPI that serves predictions from a pre-trained Linear Regression model.

## Project Structure

```
backend/
├── __init__.py          # Backend package initialization
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── models/              # Model loading and serving components
│   └── __init__.py
├── routes/              # API endpoint definitions
│   └── __init__.py
├── schemas/             # Pydantic request/response models
│   └── __init__.py
└── tests/               # Unit and integration tests
    └── __init__.py
```

## Environment Variables

The application requires the following environment variables:

### Required

- **MODEL_PATH**: Path to the trained model file (pickle or joblib format)
  - Example: `./models/linear_regression_model.pkl`

### Optional

- **PORT**: Port for the FastAPI backend server (default: 8000)
  - Must be between 1024-65535
  - Example: `8000`

- **CORS_ALLOWED_ORIGINS**: Comma-separated list of allowed origins for CORS
  - Default: `http://localhost:3000`
  - Example: `http://localhost:3000,https://example.com`

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/macOS: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Edit `.env` and set the required environment variables.

## Running the Application

### Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Using Python Directly

```bash
python main.py
```

## Running Tests

```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=backend --cov-report=html
```

## API Endpoints

### GET /
Root endpoint returning API information.

**Response:**
```json
{
  "name": "House Price Prediction API",
  "version": "1.0.0",
  "status": "running"
}
```

More endpoints will be added as development progresses.

## Dependencies

- **fastapi**: Web framework for building APIs
- **uvicorn**: ASGI server for running FastAPI
- **pydantic**: Data validation using Python type annotations
- **scikit-learn**: Machine learning library for model serving
- **python-multipart**: Support for form data parsing
- **pytest**: Testing framework
- **hypothesis**: Property-based testing library
- **python-dotenv**: Environment variable management
