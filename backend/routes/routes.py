"""
API routes for Indian Metropolitan House Price Prediction.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from schemas import (
    PropertyDetailsRequest,
    PredictionResponse,
    PriceRange,
    ConfidenceMetrics,
    OptionsResponse,
    ModelInfoResponse,
    HealthResponse,
    ErrorResponse
)
from utils import sanitize_location
from models import ModelServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global model server instance (initialized by main.py)
model_server: ModelServer = None


def set_model_server(ms: ModelServer) -> None:
    """Set the global model server instance."""
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
    Predict Indian house price based on property characteristics.
    
    Args:
        request: PropertyDetailsRequest with Indian property characteristics
        
    Returns:
        PredictionResponse with predicted price in INR, empirical 90% range, and currency INR
    """
    if model_server is None or not model_server.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="prediction service unavailable"
        )

    try:
        # Sanitize location/locality string
        sanitized_locality = sanitize_location(request.locality)
        
        property_data = {
            "area_sqft": request.area_sqft,
            "bhk": request.bhk,
            "bathrooms": request.bathrooms,
            "city": request.city,
            "locality": sanitized_locality,
            "property_type": request.property_type,
            "furnishing": request.furnishing
        }
        
        try:
            predicted_price, lower_bound, upper_bound = model_server.predict(property_data)
        except ValueError as e:
            error_msg = str(e)
            logger.warning(f"Prediction input error: {error_msg}")
            
            if "Unsupported city" in error_msg or "Unknown feature" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="prediction service unavailable"
            )
        
        return PredictionResponse(
            predicted_price=predicted_price,
            price_range=PriceRange(
                lower=lower_bound,
                upper=upper_bound
            ),
            currency="INR",
            confidence_metrics=ConfidenceMetrics(
                confidence_interval={
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound
                }
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="prediction service unavailable"
        )


@router.get(
    "/options",
    response_model=OptionsResponse,
    status_code=status.HTTP_200_OK
)
async def get_options() -> OptionsResponse:
    """
    Return available cities, localities by city, property types, and furnishing types.
    """
    if model_server is None:
        return OptionsResponse(
            cities=[],
            localities={},
            property_types=[],
            furnishing_types=[]
        )
    
    opts = model_server.get_options()
    return OptionsResponse(**opts)


@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    status_code=status.HTTP_200_OK
)
async def get_model_info() -> ModelInfoResponse:
    """
    Return model metadata, benchmark table (Linear Regression, Random Forest, Gradient Boosting),
    empirical prediction interval ratios, and training dataset documentation.
    """
    if model_server is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model metadata unavailable"
        )
    
    info = model_server.get_model_info()
    return ModelInfoResponse(**info)


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
    """
    is_model_loaded = model_server is not None and model_server.is_loaded
    
    if not is_model_loaded:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "model_loaded": False
            }
        )
    
    return HealthResponse(
        status="healthy",
        model_loaded=True
    )
