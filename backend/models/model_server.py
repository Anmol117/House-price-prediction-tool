"""
Model Server component for loading and serving predictions from trained ML model.
"""

import os
import sys
import pickle
import joblib
import logging
from typing import Dict, Tuple, Optional
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelServer:
    """
    Model Server for loading, validating, and serving predictions from trained Linear Regression model.
    
    Attributes:
        model: scikit-learn LinearRegression instance
        feature_names: List of expected feature names in correct order
        is_loaded: Boolean indicating successful model load
        
    Requirements: 6.1-6.7
    """
    
    def __init__(self):
        """Initialize ModelServer with empty state."""
        self.model: Optional[object] = None
        self.feature_names: list[str] = [
            "square_footage",
            "bedrooms",
            "bathrooms",
            "location_encoded",  # Assuming location is encoded in model
            "year_built"
        ]
        self.is_loaded: bool = False
    
    def load_model(self, path: str) -> None:
        """
        Load model from pickle or joblib file.
        
        Args:
            path: Path to the model file
            
        Raises:
            FileNotFoundError: If model file not found
            Exception: If model fails to deserialize or validate
            
        Requirements: 6.1, 6.2, 6.6
        """
        if not os.path.exists(path):
            error_msg = f"Model file not found at {path}"
            logger.error(error_msg)
            print(error_msg, file=sys.stderr)
            sys.exit(1)
        
        try:
            # Try loading with joblib first, then pickle
            try:
                self.model = joblib.load(path)
            except Exception:
                with open(path, 'rb') as f:
                    self.model = pickle.load(f)
            
            # Validate the loaded model
            if not self.validate_model():
                error_msg = "Invalid model file format"
                logger.error(error_msg)
                print(error_msg, file=sys.stderr)
                sys.exit(1)
            
            self.is_loaded = True
            logger.info("Model loaded successfully")
            print("Model loaded successfully")
            
        except (pickle.UnpicklingError, Exception) as e:
            error_msg = f"Invalid model file format: {str(e)}"
            logger.error(error_msg)
            print("Invalid model file format", file=sys.stderr)
            sys.exit(1)
    
    def validate_model(self) -> bool:
        """
        Verify model has required attributes.
        
        Returns:
            True if model is valid, False otherwise
            
        Requirements: 6.6
        """
        if self.model is None:
            return False
        
        # Check for required methods and attributes
        required_attrs = ['predict']
        
        for attr in required_attrs:
            if not hasattr(self.model, attr):
                logger.error(f"Model missing required attribute: {attr}")
                return False
        
        # For Linear Regression, check for coefficients (optional validation)
        if hasattr(self.model, 'coef_') and hasattr(self.model, 'intercept_'):
            logger.info("Model validated: Linear Regression with coefficients found")
        
        return True
    
    def transform_input(self, data: Dict) -> np.ndarray:
        """
        Convert request data to model input format.
        
        Transforms property details dictionary to numpy array in the correct
        feature order matching training data format.
        
        Args:
            data: Dictionary with property details
            
        Returns:
            Numpy array ready for model prediction
            
        Raises:
            ValueError: If data contains unknown features
            
        Requirements: 6.4, 6.7
        """
        # Check for unknown features
        expected_keys = {"square_footage", "bedrooms", "bathrooms", "location", "year_built"}
        provided_keys = set(data.keys())
        
        unknown_features = provided_keys - expected_keys
        if unknown_features:
            unknown = ', '.join(unknown_features)
            raise ValueError(f"Unknown feature: {unknown}")
        
        # For now, we'll do a simple encoding of location
        # In a real implementation, this would use the same encoding as training
        # For simplicity, we'll use a hash-based encoding
        location_encoded = hash(data.get("location", "")) % 1000
        
        # Create array in correct feature order
        features = np.array([[
            float(data["square_footage"]),
            float(data["bedrooms"]),
            float(data["bathrooms"]),
            float(location_encoded),
            float(data["year_built"])
        ]])
        
        return features
    
    def predict(self, data: Dict) -> float:
        """
        Generate price prediction from property details.
        
        Args:
            data: Dictionary with property details (square_footage, bedrooms, bathrooms, location, year_built)
            
        Returns:
            Predicted price as float
            
        Raises:
            ValueError: If model not loaded or invalid input
            
        Requirements: 2.3, 6.5
        """
        if not self.is_loaded or self.model is None:
            raise ValueError("Model not loaded")
        
        # Transform input to model format
        features = self.transform_input(data)
        
        # Generate prediction
        prediction = self.model.predict(features)
        
        # Return single float value
        return float(prediction[0])
    
    def calculate_confidence_interval(self, prediction: float) -> Tuple[float, float]:
        """
        Calculate confidence interval for prediction.
        
        For a simple implementation, we'll use a fixed percentage range.
        In a production system, this would use actual model uncertainty estimates.
        
        Args:
            prediction: The predicted price
            
        Returns:
            Tuple of (lower_bound, upper_bound)
            
        Requirements: 11.3
        """
        # Use +/- 10% as confidence interval (simplified)
        margin = prediction * 0.10
        lower_bound = prediction - margin
        upper_bound = prediction + margin
        
        # Ensure bounds are non-negative
        lower_bound = max(0, lower_bound)
        
        return (lower_bound, upper_bound)
