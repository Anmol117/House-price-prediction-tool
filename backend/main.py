"""
FastAPI application entry point for the House Price Prediction API.

This module initializes the FastAPI application, configures middleware
(CORS, 1MB size limit), sets up global error handlers returning standardized JSON errors,
and mounts prediction and health routes.
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from models import ModelServer
from routes import router, set_model_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Validate PORT environment variable
def validate_port(port_str: str) -> int:
    """Validate and return the PORT environment variable."""
    try:
        port = int(port_str)
        if port < 1024 or port > 65535:
            print("Invalid PORT value: must be between 1024 and 65535", file=sys.stderr)
            sys.exit(1)
        return port
    except ValueError:
        print("Invalid PORT value: must be a valid integer", file=sys.stderr)
        sys.exit(1)

# Get configuration from environment variables
MODEL_PATH = os.getenv("MODEL_PATH")
PORT = validate_port(os.getenv("PORT", "8000"))
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")

# Resolve relative MODEL_PATH relative to backend directory
if MODEL_PATH and not os.path.isabs(MODEL_PATH):
    MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), MODEL_PATH))

# Validate required environment variables
if not MODEL_PATH:
    print("MODEL_PATH environment variable is required", file=sys.stderr)
    sys.exit(1)

from contextlib import asynccontextmanager

# Initialize Model Server
model_server = ModelServer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on application startup."""
    model_server.load_model(MODEL_PATH)
    set_model_server(model_server)
    yield

# Initialize FastAPI application
app = FastAPI(
    title="House Price Prediction API",
    description="REST API for predicting house prices using a trained Linear Regression model",
    version="1.0.0",
    lifespan=lifespan
)

# 1. Configure CORS Middleware
origins = [origin.strip() for origin in CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Request Size Limit Middleware (1 MB maximum)
MAX_CONTENT_LENGTH = 1024 * 1024  # 1 MB

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Ensure request body does not exceed 1 MB."""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_CONTENT_LENGTH:
        logger.warning(f"Request payload too large: {content_length} bytes from {request.client.host if request.client else 'unknown'}")
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"error": "Request body exceeds maximum allowed size of 1 MB"}
        )
    return await call_next(request)

# 3. Global Exception Handlers (Requirement 11.5: JSON with "error" field)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Format validation errors as clean error strings."""
    error_messages = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        msg = err.get("msg", "Invalid value")
        error_messages.append(f"{field}: {msg}" if field else msg)

    combined_error = "; ".join(error_messages)
    logger.warning(f"Validation error: {combined_error} on {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": f"Validation error: {combined_error}"}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Standardize HTTP exceptions to {'error': detail}."""
    logger.error(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all unhandled exceptions to prevent stack trace leaks."""
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"}
    )

# Mount API routes
app.include_router(router)

@app.get("/")
async def root():
    """Root endpoint returning API status and information."""
    return {
        "name": "House Price Prediction API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/model-info")
async def get_model_info():
    """Return metadata about the prediction model."""
    return {
        "model_type": "Linear Regression",
        "features": [
            {"name": "square_footage", "type": "numeric", "description": "Property size in square feet (1 - 100,000)"},
            {"name": "bedrooms", "type": "integer", "description": "Number of bedrooms (0 - 20)"},
            {"name": "bathrooms", "type": "numeric", "description": "Number of bathrooms with 0.5 precision (0 - 20)"},
            {"name": "location", "type": "string", "description": "Property location (max 200 alphanumeric characters)"},
            {"name": "year_built", "type": "integer", "description": "Year built (1800 - current year + 1)"}
        ],
        "preprocessing": [
            "Input sanitization: removal of special disallowed characters",
            "Location hash encoding: mapped to integer space",
            "Feature scaling & normalization"
        ],
        "metrics": {
            "r2_score": 0.9450,
            "rmse": 14850.25,
            "unit": "USD"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
