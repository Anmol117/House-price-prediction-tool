"""
Pydantic models for API request and response validation.
"""

import re
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class PropertyDetailsRequest(BaseModel):
    """
    Request model for property details used in price prediction.
    
    Validates all property input fields according to requirements:
    - square_footage: 1-100000
    - bedrooms: 0-20
    - bathrooms: 0-20
    - location: max 200 chars, alphanumeric + spaces, commas, periods, hyphens, apostrophes
    - year_built: 1800 to current_year+1
    
    Requirements: 2.2, 10.1-10.6, 11.1
    """
    
    square_footage: float = Field(
        ...,
        ge=1,
        le=100000,
        description="Square footage of the property (1-100000)"
    )
    
    bedrooms: int = Field(
        ...,
        ge=0,
        le=20,
        description="Number of bedrooms (0-20)"
    )
    
    bathrooms: float = Field(
        ...,
        ge=0,
        le=20,
        description="Number of bathrooms (0-20)"
    )
    
    location: str = Field(
        ...,
        max_length=200,
        description="Property location (max 200 characters)"
    )
    
    year_built: int = Field(
        ...,
        ge=1800,
        description="Year the property was built (1800-present)"
    )
    
    @field_validator('location')
    @classmethod
    def validate_location_characters(cls, v: str) -> str:
        """
        Validate that location contains only allowed characters:
        alphanumeric, spaces, commas, periods, hyphens, apostrophes.
        
        Requirements: 10.5
        """
        if not v:
            return v
        
        # Pattern to check if string contains only allowed characters
        pattern = r"^[a-zA-Z0-9 ,.\-']+$"
        
        if not re.match(pattern, v):
            raise ValueError(
                "Location must contain only alphanumeric characters, spaces, "
                "commas, periods, hyphens, and apostrophes"
            )
        
        return v
    
    @field_validator('year_built')
    @classmethod
    def validate_year_built_max(cls, v: int) -> int:
        """
        Validate that year_built is not greater than current_year + 1.
        
        Requirements: 10.4
        """
        current_year = datetime.now().year
        max_year = current_year + 1
        
        if v > max_year:
            raise ValueError(
                f"Year built must be between 1800 and {max_year}"
            )
        
        return v
    
    model_config = {
        # Ensure field names are case-sensitive and exact
        "extra": "forbid",  # Reject unknown fields
    }


class ConfidenceMetrics(BaseModel):
    """
    Model for confidence metrics in prediction response.
    
    Requirements: 11.3
    """
    
    confidence_interval: dict[str, float] = Field(
        ...,
        description="Confidence interval with lower_bound and upper_bound"
    )
    
    @field_validator('confidence_interval')
    @classmethod
    def validate_confidence_interval_structure(cls, v: dict) -> dict:
        """Ensure confidence_interval has required keys."""
        if 'lower_bound' not in v or 'upper_bound' not in v:
            raise ValueError(
                "confidence_interval must contain 'lower_bound' and 'upper_bound' keys"
            )
        
        return v


class PredictionResponse(BaseModel):
    """
    Response model for price prediction.
    
    Requirements: 11.2, 11.3
    """
    
    predicted_price: float = Field(
        ...,
        description="Predicted house price rounded to 2 decimal places"
    )
    
    confidence_metrics: ConfidenceMetrics = Field(
        ...,
        description="Confidence metrics including confidence interval"
    )


class HealthResponse(BaseModel):
    """
    Response model for health check endpoint.
    
    Requirements: 11.4
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
    
    Requirements: 11.5
    """
    
    error: str = Field(
        ...,
        description="Descriptive error message"
    )
