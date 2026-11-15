"""
Unit tests for API routes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from routes import set_model_server
from models import ModelServer


@pytest.fixture
def mock_model_server():
    """Create a mock ModelServer for testing."""
    mock_server = Mock(spec=ModelServer)
    mock_server.is_loaded = True
    mock_server.predict = Mock(return_value=(8200000.00, 3353800.00, 23460200.00))
    mock_server.calculate_confidence_interval = Mock(return_value=(3353800.00, 23460200.00))
    mock_server.get_options = Mock(return_value={
        "cities": ["Bengaluru", "Mumbai", "Pune"],
        "localities": {"Pune": ["Wakad", "Baner", "Other"]},
        "property_types": ["Apartment", "Villa"],
        "furnishing_types": ["Furnished", "Semi-furnished", "Unfurnished"]
    })
    mock_server.get_model_info = Mock(return_value={
        "best_model": "Random Forest",
        "features": ["area_sqft", "bhk", "bathrooms", "city", "locality", "property_type", "furnishing"],
        "benchmark": [
            {"model": "Linear Regression", "r2": 0.1502, "mae": 4817168.01, "rmse": 13049671.28},
            {"model": "Random Forest", "r2": 0.4278, "mae": 4752048.42, "rmse": 10708244.89},
            {"model": "Gradient Boosting", "r2": 0.3656, "mae": 4802673.11, "rmse": 11274847.46}
        ],
        "interval_ratios": {"lower": 0.409, "upper": 2.861},
        "dataset_summary": {"total_records": 29624}
    })
    return mock_server


@pytest.fixture
def client(mock_model_server):
    """Create test client with mocked model server."""
    set_model_server(mock_model_server)
    return TestClient(app)


class TestPredictEndpoint:
    """Test cases for POST /predict endpoint."""
    
    def test_predict_valid_indian_input(self, client, mock_model_server):
        """Test prediction with valid Indian property details."""
        request_data = {
            "area_sqft": 1150.0,
            "bhk": 2,
            "bathrooms": 2.0,
            "city": "Pune",
            "locality": "Wakad",
            "property_type": "Apartment",
            "furnishing": "Semi-furnished"
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "predicted_price" in data
        assert "price_range" in data
        assert data["currency"] == "INR"
        assert "lower" in data["price_range"]
        assert "upper" in data["price_range"]
        assert data["predicted_price"] == 8200000.00
        assert data["price_range"]["lower"] == 3353800.00
        assert data["price_range"]["upper"] == 23460200.00
        
        # Check backward compatibility fields
        assert "confidence_metrics" in data
        assert "lower_bound" in data["confidence_metrics"]["confidence_interval"]
    
    def test_predict_missing_field(self, client):
        """Test prediction with missing required field."""
        request_data = {
            "area_sqft": 1150.0,
            "bhk": 2,
            "bathrooms": 2.0,
            # city is missing
            "locality": "Wakad",
            "property_type": "Apartment",
            "furnishing": "Semi-furnished"
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 400
        assert "error" in response.json()
    
    def test_predict_invalid_area_sqft(self, client):
        """Test prediction with out-of-range area_sqft."""
        request_data = {
            "area_sqft": 50000.0,  # Exceeds max 20000
            "bhk": 2,
            "bathrooms": 2.0,
            "city": "Pune",
            "locality": "Wakad",
            "property_type": "Apartment",
            "furnishing": "Semi-furnished"
        }
        
        response = client.post("/predict", json=request_data)
        assert response.status_code == 400
        assert "error" in response.json()

    def test_predict_invalid_bhk(self, client):
        """Test prediction with out-of-range bhk."""
        request_data = {
            "area_sqft": 1200.0,
            "bhk": 15,  # Exceeds max 10
            "bathrooms": 2.0,
            "city": "Pune",
            "locality": "Wakad",
            "property_type": "Apartment",
            "furnishing": "Semi-furnished"
        }
        
        response = client.post("/predict", json=request_data)
        assert response.status_code == 400
        assert "error" in response.json()

    def test_predict_unsupported_city(self, client, mock_model_server):
        """Test prediction when city is unsupported."""
        mock_model_server.predict.side_effect = ValueError("Unsupported city 'Atlantis'")
        
        request_data = {
            "area_sqft": 1150.0,
            "bhk": 2,
            "bathrooms": 2.0,
            "city": "Atlantis",
            "locality": "Unknown",
            "property_type": "Apartment",
            "furnishing": "Semi-furnished"
        }
        
        response = client.post("/predict", json=request_data)
        assert response.status_code == 400
        assert "Unsupported city" in response.json()["error"]
    
    def test_predict_model_failure(self, client, mock_model_server):
        """Test prediction when model fails."""
        mock_model_server.predict.side_effect = Exception("Model calculation failed")
        
        request_data = {
            "area_sqft": 1150.0,
            "bhk": 2,
            "bathrooms": 2.0,
            "city": "Pune",
            "locality": "Wakad",
            "property_type": "Apartment",
            "furnishing": "Semi-furnished"
        }
        
        response = client.post("/predict", json=request_data)
        assert response.status_code == 500


class TestOptionsEndpoint:
    """Test cases for GET /options endpoint."""

    def test_options_returns_metadata_lists(self, client, mock_model_server):
        """Test options endpoint returns cities and property types."""
        response = client.get("/options")
        assert response.status_code == 200
        data = response.json()
        assert "cities" in data
        assert "localities" in data
        assert "property_types" in data
        assert "furnishing_types" in data
        assert "Pune" in data["cities"]


class TestHealthEndpoint:
    """Test cases for GET /health endpoint."""
    
    def test_health_model_loaded(self, client, mock_model_server):
        """Test health endpoint when model is loaded."""
        mock_model_server.is_loaded = True
        set_model_server(mock_model_server)
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True
    
    def test_health_model_not_loaded(self, client):
        """Test health endpoint when model is not loaded."""
        mock_server = Mock(spec=ModelServer)
        mock_server.is_loaded = False
        set_model_server(mock_server)
        
        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["model_loaded"] is False
    
    def test_health_no_model_server(self, client):
        """Test health endpoint when model server is None."""
        set_model_server(None)
        
        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["model_loaded"] is False


class TestRealModelServerIntegration:
    """Integration test using the actual loaded model.joblib."""

    def test_real_model_prediction_pune(self):
        """Test that the real model predicts realistic prices for Wakad, Pune."""
        ms = ModelServer()
        model_path = os.path.join(os.path.dirname(__file__), "..", "models", "model.joblib")
        if not os.path.exists(model_path):
            pytest.skip("model.joblib not present")
        
        ms.load_model(model_path)
        assert ms.is_loaded is True
        
        pred, low, high = ms.predict({
            "area_sqft": 1150,
            "bhk": 2,
            "bathrooms": 2,
            "city": "Pune",
            "locality": "Wakad",
            "property_type": "Apartment",
            "furnishing": "Semi-furnished"
        })
        
        # Wakad 2 BHK should be around 70 Lakhs to 95 Lakhs (target ~82 Lakhs)
        assert 6000000 <= pred <= 11000000
        assert low < pred < high
        
        # Test determinism: same input gives exact same output
        pred2, low2, high2 = ms.predict({
            "area_sqft": 1150,
            "bhk": 2,
            "bathrooms": 2,
            "city": "Pune",
            "locality": "Wakad",
            "property_type": "Apartment",
            "furnishing": "Semi-furnished"
        })
        assert pred == pred2
        assert low == low2
        assert high == high2
