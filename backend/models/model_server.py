"""
Model Server component for loading and serving predictions from trained ML pipeline.
Configured for Indian Metropolitan Housing Price Prediction.
"""

import os
import sys
import json
import joblib
import logging
from typing import Dict, Tuple, Optional, Any
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelServer:
    """
    Model Server for loading, validating, and serving predictions from trained ML pipeline.
    
    Attributes:
        model: scikit-learn Pipeline instance
        meta: Dictionary loaded from model_meta.json
        feature_names: List of expected feature names in correct order
        is_loaded: Boolean indicating successful model load
    """
    
    def __init__(self):
        """Initialize ModelServer with empty state."""
        self.model: Optional[object] = None
        self.meta: Dict[str, Any] = {}
        self.feature_names: list[str] = [
            "area_sqft",
            "bhk",
            "bathrooms",
            "city",
            "locality",
            "property_type",
            "furnishing"
        ]
        self.interval_ratios: Dict[str, float] = {"lower": 0.5, "upper": 2.0}
        self.cities: list[str] = []
        self.localities: Dict[str, list[str]] = {}
        self.property_types: list[str] = []
        self.furnishing_types: list[str] = []
        self.is_loaded: bool = False
    
    def load_model(self, path: str) -> None:
        """
        Load model from joblib (or pickle) and metadata from companion json.
        
        Args:
            path: Path to the model file
            
        Raises:
            FileNotFoundError: If model file not found
            Exception: If model fails to deserialize or validate
        """
        if not os.path.exists(path):
            error_msg = f"Model file not found at {path}"
            logger.error(error_msg)
            print(error_msg, file=sys.stderr)
            sys.exit(1)
        
        try:
            # Load trained pipeline
            self.model = joblib.load(path)
            
            # Load metadata
            meta_path = os.path.join(os.path.dirname(path), "model_meta.json")
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.meta = json.load(f)
                    self.interval_ratios = self.meta.get("interval_ratios", {"lower": 0.5, "upper": 2.0})
                    self.cities = self.meta.get("cities", [])
                    self.localities = self.meta.get("localities", {})
                    self.property_types = self.meta.get("property_types", [])
                    self.furnishing_types = self.meta.get("furnishing_types", [])
                    if "features" in self.meta:
                        self.feature_names = self.meta["features"]
            
            # Validate the loaded model
            if not self.validate_model():
                error_msg = "Invalid model file format"
                logger.error(error_msg)
                print(error_msg, file=sys.stderr)
                sys.exit(1)
            
            self.is_loaded = True
            logger.info("Model loaded successfully")
            print("Model loaded successfully")
            
        except Exception as e:
            error_msg = f"Invalid model file format: {str(e)}"
            logger.error(error_msg)
            print("Invalid model file format", file=sys.stderr)
            sys.exit(1)
    
    def validate_model(self) -> bool:
        """
        Verify model has required attributes.
        
        Returns:
            True if model is valid, False otherwise
        """
        if self.model is None:
            return False
        
        required_attrs = ['predict']
        for attr in required_attrs:
            if not hasattr(self.model, attr):
                logger.error(f"Model missing required attribute: {attr}")
                return False
        
        return True
    
    def transform_input(self, data: Dict) -> pd.DataFrame:
        """
        Convert request data to pandas DataFrame format matching model pipeline.
        
        Args:
            data: Dictionary with property details
            
        Returns:
            1-row DataFrame ready for model prediction
            
        Raises:
            ValueError: If data contains unknown features or unsupported city
        """
        expected_keys = set(self.feature_names)
        provided_keys = set(data.keys())
        
        unknown_features = provided_keys - expected_keys
        if unknown_features:
            unknown = ', '.join(sorted(unknown_features))
            raise ValueError(f"Unknown feature: {unknown}")
        
        city = str(data.get("city", "")).strip()
        if self.cities and city not in self.cities:
            raise ValueError(f"Unsupported city '{city}'. Supported cities: {', '.join(self.cities)}")
        
        locality = str(data.get("locality", "")).strip()
        # If locality not in known list for this city, map to 'Other' if available, else retain
        city_locs = self.localities.get(city, [])
        if city_locs and locality not in city_locs:
            if "Other" in city_locs:
                locality = "Other"
        
        row = {
            "area_sqft": float(data["area_sqft"]),
            "bhk": int(data["bhk"]),
            "bathrooms": float(data["bathrooms"]),
            "city": city,
            "locality": locality,
            "property_type": str(data.get("property_type", "Apartment")).strip(),
            "furnishing": str(data.get("furnishing", "Semi-furnished")).strip()
        }
        
        return pd.DataFrame([row])
    
    def predict(self, data: Dict) -> Tuple[float, float, float]:
        """
        Generate price prediction and empirical interval from property details.
        
        Args:
            data: Dictionary with property details
            
        Returns:
            Tuple of (predicted_price, lower_bound, upper_bound) in INR
            
        Raises:
            ValueError: If model not loaded or invalid input
        """
        if not self.is_loaded or self.model is None:
            raise ValueError("Model not loaded")
        
        df_features = self.transform_input(data)
        
        # Pipeline predicts log(price)
        pred_log = self.model.predict(df_features)
        raw_pred = float(np.expm1(pred_log[0]))
        
        # Enforce realistic lower bound (at least 1 Lakh INR)
        predicted_price = round(max(raw_pred, 100000.0), 2)
        
        # Empirical prediction interval using test set residual ratios
        low_ratio = self.interval_ratios.get("lower", 0.5)
        high_ratio = self.interval_ratios.get("upper", 2.0)
        
        lower_bound = round(predicted_price * low_ratio, 2)
        upper_bound = round(predicted_price * high_ratio, 2)
        
        return predicted_price, lower_bound, upper_bound
    
    def calculate_confidence_interval(self, prediction: float) -> Tuple[float, float]:
        """
        Calculate empirical prediction interval for prediction.
        
        Args:
            prediction: The predicted price in INR
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        low_ratio = self.interval_ratios.get("lower", 0.5)
        high_ratio = self.interval_ratios.get("upper", 2.0)
        
        lower_bound = round(prediction * low_ratio, 2)
        upper_bound = round(prediction * high_ratio, 2)
        
        return (lower_bound, upper_bound)
    
    def get_options(self) -> Dict[str, Any]:
        """Return available dropdown options for the frontend."""
        return {
            "cities": self.cities,
            "localities": self.localities,
            "property_types": self.property_types,
            "furnishing_types": self.furnishing_types
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata, benchmark table, and dataset documentation."""
        return {
            "best_model": self.meta.get("best_model", "Random Forest"),
            "features": self.feature_names,
            "benchmark": self.meta.get("benchmark", []),
            "interval_ratios": self.interval_ratios,
            "dataset_summary": self.meta.get("dataset_summary", {})
        }
