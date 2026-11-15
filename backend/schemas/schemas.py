"""
Pydantic models for API request and response validation.
Configured for Indian Residential Property Market.
"""

from typing import Literal, Optional, Dict, List, Any
from pydantic import BaseModel, Field, field_validator


class PropertyDetailsRequest(BaseModel):
    """
    Request model for property details used in price prediction.
    
    Validates all property input fields according to Indian market requirements:
    - area_sqft: 200 - 20,000 sq ft
    - bhk: 1 - 10 BHK
    - bathrooms: 1 - 10 bathrooms
    - city: non-empty string, e.g. "Pune", "Bengaluru", "Mumbai", etc.
    - locality: non-empty string, e.g. "Wakad", "Whitefield", "Andheri West", etc.
    - property_type: "Apartment", "Builder Floor", "Independent House", "Villa"
    - furnishing: "Furnished", "Semi-furnished", "Unfurnished"
    """
    
    area_sqft: float = Field(
        ...,
        ge=200,
        le=20000,
        description="Super built-up / carpet area in square feet (200 - 20,000)"
    )
    
    bhk: int = Field(
        ...,
        ge=1,
        le=10,
        description="Number of bedrooms / BHK (1 - 10)"
    )
    
    bathrooms: float = Field(
        ...,
        ge=1,
        le=10,
        description="Number of bathrooms (1 - 10)"
    )
    
    city: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="City name (e.g. Pune, Bengaluru, Mumbai)"
    )
    
    locality: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Locality / Neighborhood name within the city"
    )
    
    property_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Property type (Apartment, Builder Floor, Independent House, Villa)"
    )
    
    furnishing: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Furnishing status (Furnished, Semi-furnished, Unfurnished)"
    )
    
    @field_validator('city', 'locality', 'property_type', 'furnishing')
    @classmethod
    def strip_and_validate_non_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Field cannot be empty or whitespace only")
        return stripped

    model_config = {
        "extra": "forbid",  # Reject unknown fields
    }


class PriceRange(BaseModel):
    """
    Empirical 90% prediction interval for the estimated price.
    """
    lower: float = Field(..., description="Lower bound of predicted price in INR")
    upper: float = Field(..., description="Upper bound of predicted price in INR")


class ConfidenceMetrics(BaseModel):
    """
    Model for confidence metrics in prediction response.
    Maintains compatibility with lower_bound/upper_bound structure.
    """
    confidence_interval: Dict[str, float] = Field(
        ...,
        description="Confidence interval with lower_bound and upper_bound"
    )
    
    @field_validator('confidence_interval')
    @classmethod
    def validate_confidence_interval_structure(cls, v: dict) -> dict:
        if 'lower_bound' not in v or 'upper_bound' not in v:
            raise ValueError(
                "confidence_interval must contain 'lower_bound' and 'upper_bound' keys"
            )
        return v


class PredictionResponse(BaseModel):
    """
    Response model for price prediction.
    """
    predicted_price: float = Field(
        ...,
        description="Predicted house price in INR rounded to 2 decimal places"
    )
    price_range: PriceRange = Field(
        ...,
        description="Empirical 90% prediction interval [lower, upper] in INR"
    )
    currency: str = Field(
        default="INR",
        description="Currency code (INR)"
    )
    confidence_metrics: ConfidenceMetrics = Field(
        ...,
        description="Confidence metrics containing lower_bound and upper_bound"
    )


class OptionsResponse(BaseModel):
    """
    Response model for available dropdown options.
    """
    cities: List[str] = Field(..., description="List of supported Indian cities")
    localities: Dict[str, List[str]] = Field(..., description="Mapping of city to localities")
    property_types: List[str] = Field(..., description="List of property types")
    furnishing_types: List[str] = Field(..., description="List of furnishing types")


class BenchmarkItem(BaseModel):
    """
    Model comparison benchmark item.
    """
    model: str
    r2: float
    mae: float
    rmse: float


class ModelInfoResponse(BaseModel):
    """
    Response model for model comparison and dataset documentation.
    """
    best_model: str
    features: List[str]
    benchmark: List[BenchmarkItem]
    interval_ratios: Dict[str, float]
    dataset_summary: Dict[str, Any]


class HealthResponse(BaseModel):
    """
    Response model for health check endpoint.
    """
    status: Literal["healthy", "unhealthy"] = Field(
        ...,
        description="Health status of the service"
    )
    model_loaded: bool = Field(
        ...,
        description="Whether the ML model is loaded in memory"
    )

    model_config = {
        "protected_namespaces": ()
    }


class ErrorResponse(BaseModel):
    """
    Response model for error responses.
    """
    error: str = Field(
        ...,
        description="Descriptive error message"
    )
