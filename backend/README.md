# HomeValuate AI — Backend API

REST API built with **FastAPI** and **scikit-learn** to predict residential property prices in Indian metropolitan regions.

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── prepare_dataset.py   # Dataset ingestion and cleaning script
├── train_model.py       # Model training and 3-model benchmark script
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── data/
│   └── india_housing.csv # Cleaned Indian housing dataset (29,624 records)
├── models/              # Model pipeline and server
│   ├── model.joblib     # Serialized production pipeline
│   ├── model_meta.json  # Metadata, benchmarks, and option lists
│   └── model_server.py  # Model inference and interval calculation
├── routes/              # FastAPI routers
│   └── routes.py        # /predict, /options, /model-info, /health
├── schemas/             # Pydantic validation schemas
│   └── schemas.py
└── tests/               # Unit and integration tests
    ├── test_main.py
    ├── test_routes.py
    └── test_utils.py
```

## Running the Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Download dataset
python prepare_dataset.py

# Train & benchmark models
python train_model.py

# Run tests
pytest

# Start server
uvicorn main:app --reload --port 8000
```
