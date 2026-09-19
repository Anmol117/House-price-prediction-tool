# Backend Dockerfile for House Price Prediction API
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Ensure model exists or train if missing
RUN python train_model.py

ENV PORT=8000
ENV MODEL_PATH=models/model.pkl
ENV CORS_ALLOWED_ORIGINS=http://localhost:3000

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
