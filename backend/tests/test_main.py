"""
Unit tests for main.py application initialization, configuration, and middleware.
"""

import os
import sys
import pytest
from unittest import mock

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from main import validate_port, app
except ImportError:
    from backend.main import validate_port, app


def test_validate_port_valid():
    """Test that validate_port accepts valid port numbers."""
    assert validate_port("8000") == 8000
    assert validate_port("1024") == 1024
    assert validate_port("65535") == 65535


def test_validate_port_out_of_range():
    """Test that validate_port rejects out of range ports."""
    with pytest.raises(SystemExit) as exc_info:
        validate_port("1023")
    assert exc_info.value.code == 1
    
    with pytest.raises(SystemExit) as exc_info:
        validate_port("65536")
    assert exc_info.value.code == 1


def test_validate_port_invalid():
    """Test that validate_port rejects non-numeric ports."""
    with pytest.raises(SystemExit) as exc_info:
        validate_port("abc")
    assert exc_info.value.code == 1


def test_root_endpoint():
    """Test that root GET / endpoint returns 200."""
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_model_info_endpoint():
    """Test that GET /model-info returns 200 and model details."""
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_type"] == "Linear Regression"
    assert len(data["features"]) == 5
