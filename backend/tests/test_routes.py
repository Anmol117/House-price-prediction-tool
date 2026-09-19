"""
Unit tests for API routes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
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
    mock_server.predict = Mock(return_value=850000.00)
    mock_server.calculate_confidence_interval = Mock(return_value=(800000.00, 900000.00))
    return mock_server


@pytest.fixture
def client(mock_model_server):
    """Create test client with mocked model server."""
    set_model_server(mock_model_server)
    return TestClient(app)


class TestPredictEndpoint:
    """Test cases for POST /predict endpoint."""
    
    def test_predict_valid_input(self, client, mock_model_server):
        """Test prediction with valid property details."""
        request_data = {
            "square_footage": 2500.0,
            "bedrooms": 4,
            "bathrooms": 2.5,
            "location": "San Francisco, CA",
            "year_built": 2015
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "predicted_price" in data
        assert "confidence_metrics" in data
        assert "confidence_interval" in data["confidence_metrics"]
        assert "lower_bound" in data["confidence_metrics"]["confidence_interval"]
        assert "upper_bound" in data["confidence_metrics"]["confidence_interval"]
        
        # Verify values are rounded to 2 decimal places
        assert isinstance(data["predicted_price"], float)
        assert data["predicted_price"] == 850000.00
    
    def test_predict_missing_field(self, client):
        """Test prediction with missing required field."""
        request_data = {
            "square_footage": 2500.0,
            "bedrooms": 4,
            "bathrooms": 2.5,
            # location is missing
            "year_built": 2015
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 400
        assert "error" in response.json()
    
    def test_predict_invalid_square_footage(self, client):
        """Test prediction with out-of-range square_footage."""
        request_data = {
            "square_footage": 150000.0,  # Exceeds max of 100000
            "bedrooms": 4,
            "bathrooms": 2.5,
            "location": "San Francisco, CA",
            "year_built": 2015
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 400
        assert "error" in response.json()
    
    def test_predict_invalid_bedrooms(self, client):
        """Test prediction with out-of-range bedrooms."""
        request_data = {
            "square_footage": 2500.0,
            "bedrooms": 25,  # Exceeds max of 20
            "bathrooms": 2.5,
            "location": "San Francisco, CA",
            "year_built": 2015
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 400
        assert "error" in response.json()
    
    def test_predict_invalid_year_built(self, client):
        """Test prediction with year_built too far in future."""
        request_data = {
            "square_footage": 2500.0,
            "bedrooms": 4,
            "bathrooms": 2.5,
            "location": "San Francisco, CA",
            "year_built": 2050  # Too far in future
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 400
        assert "error" in response.json()
    
    def test_predict_invalid_location_characters(self, client):
        """Test prediction with invalid characters in location."""
        request_data = {
            "square_footage": 2500.0,
            "bedrooms": 4,
            "bathrooms": 2.5,
            "location": "San Francisco @ CA #123",  # Invalid characters
            "year_built": 2015
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 400
        assert "error" in response.json()
    
    def test_predict_model_failure(self, client, mock_model_server):
        """Test prediction when model fails."""
        mock_model_server.predict.side_effect = Exception("Model error")
        
        request_data = {
            "square_footage": 2500.0,
            "bedrooms": 4,
            "bathrooms": 2.5,
            "location": "San Francisco, CA",
            "year_built": 2015
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 500
    
    def test_predict_sanitizes_location(self, client, mock_model_server):
        """Test that location is sanitized before prediction."""
        request_data = {
            "square_footage": 2500.0,
            "bedrooms": 4,
            "bathrooms": 2.5,
            "location": "San Francisco, CA",
            "year_built": 2015
        }
        
        response = client.post("/predict", json=request_data)
        
        # Should succeed
        assert response.status_code == 200
        
        # Verify predict was called (location would have been sanitized)
        mock_model_server.predict.assert_called_once()


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


class TestResponseFormat:
    """Test cases for response format validation."""
    
    def test_predicted_price_rounded_to_2_decimals(self, client, mock_model_server):
        """Test that predicted_price is rounded to 2 decimal places."""
        # Return a price with more than 2 decimals
        mock_model_server.predict.return_value = 850123.456789
        mock_model_server.calculate_confidence_interval.return_value = (
            800000.123456,
            900000.987654
        )
        
        request_data = {
            "square_footage": 2500.0,
            "bedrooms": 4,
            "bathrooms": 2.5,
            "location": "San Francisco, CA",
            "year_built": 2015
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify rounding to 2 decimal places
        assert data["predicted_price"] == 850123.46
        assert data["confidence_metrics"]["confidence_interval"]["lower_bound"] == 800000.12
        assert data["confidence_metrics"]["confidence_interval"]["upper_bound"] == 900000.99
    
    def test_response_structure(self, client, mock_model_server):
        """Test that response has correct structure."""
        request_data = {
            "square_footage": 2500.0,
            "bedrooms": 4,
            "bathrooms": 2.5,
            "location": "San Francisco, CA",
            "year_built": 2015
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure matches PredictionResponse schema
        assert set(data.keys()) == {"predicted_price", "confidence_metrics"}
        assert set(data["confidence_metrics"].keys()) == {"confidence_interval"}
        assert set(data["confidence_metrics"]["confidence_interval"].keys()) == {
            "lower_bound",
            "upper_bound"
        }
