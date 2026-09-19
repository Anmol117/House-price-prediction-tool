"""
API routes for house price prediction endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from schemas import (
    PropertyDetailsRequest,
    PredictionResponse,
    HealthResponse,
    ErrorResponse,
    ConfidenceMetrics
)
from utils import sanitize_location
from models import ModelServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global model server instance (will be initialized by main.py)
model_server: ModelServer = None


def set_model_server(ms: ModelServer) -> None:
    """
    Set the global model server instance.
    
    Args:
        ms: ModelServer instance to use for predictions
    """
    global model_server
    model_server = ms


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Model prediction failure"}
    }
)
async def predict(request: PropertyDetailsRequest) -> PredictionResponse:
    """
    Predict house price based on property details.
    
    Args:
        request: PropertyDetailsRequest with property characteristics
        
    Returns:
        PredictionResponse with predicted price and confidence metrics
        
    Raises:
        HTTPException: 400 for validation errors, 500 for model failures
        
    Requirements: 2.1, 2.3, 2.4, 2.5, 2.6, 5.1, 11.2, 11.3
    """
    try:
        # Sanitize location field
        sanitized_location = sanitize_location(request.location)
        
        # Prepare data for model
        property_data = {
            "square_footage": request.square_footage,
            "bedrooms": request.bedrooms,
            "bathrooms": request.bathrooms,
            "location": sanitized_location,
            "year_built": request.year_built
        }
        
        # Generate prediction
        try:
            predicted_price = model_server.predict(property_data)
        except ValueError as e:
            # Handle model prediction errors
            error_msg = str(e)
            logger.error(f"Model prediction error: {error_msg}")
            
            # Check if it's an unknown feature error
            if "Unknown feature" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            
            # Other model errors are 500
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="prediction service unavailable"
            )
        
        # Calculate confidence interval
        lower_bound, upper_bound = model_server.calculate_confidence_interval(predicted_price)
        
        # Format predicted_price to 2 decimal places
        predicted_price_rounded = round(predicted_price, 2)
        lower_bound_rounded = round(lower_bound, 2)
        upper_bound_rounded = round(upper_bound, 2)
        
        # Return response with confidence metrics
        return PredictionResponse(
            predicted_price=predicted_price_rounded,
            confidence_metrics=ConfidenceMetrics(
                confidence_interval={
                    "lower_bound": lower_bound_rounded,
                    "upper_bound": upper_bound_rounded
                }
            )
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch all other errors and return 500
        error_msg = "prediction service unavailable"
        logger.error(f"Unexpected error in prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    responses={
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    }
)
async def health() -> HealthResponse:
    """
    Check health status of the service.
    
    Verifies that the ML model is loaded and ready to serve predictions.
    
    Returns:
        HealthResponse with status and model_loaded flag
        
    Raises:
        HTTPException: 503 if model not loaded
        
    Requirements: 5.2, 5.3, 5.4, 11.4
    """
    try:
        # Check if model is loaded
        is_model_loaded = model_server is not None and model_server.is_loaded
        
        if not is_model_loaded:
            # Return 503 if model not loaded
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "model_loaded": False
                }
            )
        
        # Return healthy status
        return HealthResponse(
            status="healthy",
            model_loaded=True
        )
        
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in health check: {str(e)}")
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "model_loaded": False
            }
        )
