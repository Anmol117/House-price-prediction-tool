# Implementation Plan: House Price Prediction Website

## Overview

This implementation plan breaks down the development of a full-stack house price prediction web application into discrete coding tasks. The application consists of a React frontend for user interaction and a Python FastAPI backend serving predictions from a pre-trained Linear Regression model. Tasks are organized to build incrementally, with early validation of core functionality through testing.

## Tasks

- [ ] 1. Set up backend project structure and core configuration
  - Create Python project directory structure (backend, models, routes, schemas, tests)
  - Create requirements.txt with dependencies: fastapi, uvicorn, pydantic, scikit-learn, python-multipart, pytest, hypothesis
  - Create .env.example file documenting MODEL_PATH, PORT, CORS_ALLOWED_ORIGINS
  - Set up environment variable loading (python-dotenv or similar)
  - Create main.py with FastAPI app initialization
  - _Requirements: 12.1, 12.2, 12.4_

- [ ] 2. Implement backend data validation schemas
  - [ ] 2.1 Create schemas.py with Pydantic models
    - Implement PropertyDetailsRequest with field validations (square_footage: 1-100000, bedrooms: 0-20, bathrooms: 0-20, location: max 200 chars with regex pattern, year_built: 1800 to current_year+1)
    - Implement ConfidenceMetrics model with confidence_interval structure
    - Implement PredictionResponse with predicted_price and confidence_metrics
    - Implement HealthResponse with status enum and model_loaded boolean
    - Implement ErrorResponse with error field
    - _Requirements: 2.2, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [ ]* 2.2 Write property test for input validation range compliance
    - **Property 1: Input Validation Range Compliance**
    - **Validates: Requirements 1.2, 1.3, 2.2, 2.5, 10.1-10.6**
    - Use hypothesis to generate random valid inputs within ranges
    - Verify Pydantic accepts all valid inputs
    - Use hypothesis to generate invalid inputs outside ranges
    - Verify Pydantic rejects invalid inputs with field-specific errors

- [ ] 3. Implement Model Server component
  - [ ] 3.1 Create model_server.py with ModelServer class
    - Implement __init__ method to initialize attributes (model, feature_names, is_loaded)
    - Implement load_model(path) method to load pickle/joblib file with error handling
    - Implement validate_model() method to verify model has required attributes (predict, coef_, intercept_)
    - Implement transform_input(data) method to convert dict to numpy array in correct feature order
    - Implement predict(data) method to generate price prediction
    - Implement calculate_confidence_interval(prediction) method returning lower_bound and upper_bound
    - Add logging for model load success/failure to stdout/stderr
    - Add startup validation: exit with non-zero status if MODEL_PATH not found or invalid
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 12.7_
  
  - [ ]* 3.2 Write property test for prediction generation
    - **Property 4: Prediction Generation for Valid Inputs**
    - **Validates: Requirements 2.3, 6.5**
    - Use hypothesis to generate valid property details
    - Verify Model_Server returns numeric prediction within 1 second
  
  - [ ]* 3.3 Write property test for input transformation correctness
    - **Property 10: Input Transformation Correctness**
    - **Validates: Requirements 6.4**
    - Use hypothesis to generate valid property details
    - Verify transform_input produces numpy array with correct shape, order, and data types

- [ ] 4. Implement input sanitization
  - [ ] 4.1 Create utils.py with sanitization functions
    - Implement sanitize_location(location) function to remove/escape invalid characters
    - Keep only alphanumeric, spaces, commas, periods, hyphens, apostrophes
    - _Requirements: 10.8_
  
  - [ ]* 4.2 Write property test for location string sanitization
    - **Property 11: Location String Sanitization**
    - **Validates: Requirements 10.8**
    - Use hypothesis to generate location strings with mixed valid/invalid characters
    - Verify sanitization removes all invalid characters

- [ ] 5. Implement API routes
  - [ ] 5.1 Create routes.py with FastAPI router
    - Implement POST /predict endpoint accepting PropertyDetailsRequest
    - Call sanitize_location on location field
    - Call ModelServer.predict with sanitized data
    - Format predicted_price to 2 decimal places
    - Return PredictionResponse with confidence_metrics
    - Add error handling for validation errors (400), model failures (500)
    - Implement GET /health endpoint checking ModelServer.is_loaded
    - Return HealthResponse with status "healthy"/"unhealthy"
    - Return 503 if model not loaded
    - _Requirements: 2.1, 2.3, 2.4, 2.5, 2.6, 5.1, 5.2, 5.3, 5.4, 11.2, 11.3, 11.4_
  
  - [ ]* 5.2 Write property test for error response structure
    - **Property 5: Error Response Structure**
    - **Validates: Requirements 2.5, 2.6, 9.3, 10.7, 11.5**
    - Generate requests with missing fields, invalid values
    - Verify backend returns 400 with JSON containing "error" field
    - Verify error messages include field name and constraint details
    - Verify error messages do NOT include stack traces, file paths, or model internals
  
  - [ ]* 5.3 Write property test for case-sensitive field name matching
    - **Property 13: Case-Sensitive Field Name Matching**
    - **Validates: Requirements 11.1**
    - Generate requests with field names in different cases (Square_Footage, BEDROOMS, etc.)
    - Verify backend rejects requests with incorrect field name cases
  
  - [ ]* 5.4 Write property test for unknown feature detection
    - **Property 14: Unknown Feature Detection**
    - **Validates: Requirements 6.7**
    - Generate requests with extra unknown fields
    - Verify Model_Server returns error "Unknown feature: [feature_name]"

- [ ] 6. Configure FastAPI application middleware and error handlers
  - [ ] 6.1 Update main.py with middleware configuration
    - Add CORS middleware reading CORS_ALLOWED_ORIGINS from environment
    - Add request size limit middleware (1 MB maximum)
    - Register global error handlers for 400, 413, 500, 503
    - Mount routes from routes.py
    - Add startup event handler to initialize ModelServer with MODEL_PATH
    - Validate PORT environment variable (1024-65535 range, default 8000)
    - _Requirements: 5.5, 5.6, 5.7, 12.2, 12.8_
  
  - [ ]* 6.2 Write property test for malformed JSON rejection
    - **Property 12: Malformed JSON Rejection**
    - **Validates: Requirements 5.6**
    - Send requests with invalid JSON syntax to /predict endpoint
    - Verify backend returns 400 with error indicating malformed JSON
  
  - [ ]* 6.3 Write unit tests for error logging
    - **Property 9: Logging Completeness**
    - **Validates: Requirements 9.4**
    - Trigger various error conditions
    - Verify logs contain timestamp, HTTP status, endpoint, input parameters, exception type

- [ ] 7. Checkpoint - Verify backend functionality
  - Run all backend tests (pytest)
  - Manually test /health endpoint returns 200
  - Manually test /predict endpoint with valid data returns prediction
  - Manually test /predict endpoint with invalid data returns 400
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Set up frontend project structure
  - [ ] 8.1 Create React project with TypeScript
    - Initialize React app with create-react-app or vite (TypeScript template)
    - Install dependencies: react-router-dom, axios
    - Create directory structure (components, pages, utils, types)
    - Create .env.example documenting REACT_APP_API_URL
    - Set up environment variable loading for REACT_APP_API_URL
    - Add build validation to fail if REACT_APP_API_URL not set
    - _Requirements: 12.3, 12.4_

- [ ] 9. Implement frontend data models and utilities
  - [ ] 9.1 Create types.ts with TypeScript interfaces
    - Define FormData interface (all fields as strings for input handling)
    - Define ValidationErrors interface (optional field error messages)
    - Define PredictionResult interface matching backend response
    - Define ErrorObject interface with type enum and message
    - _Requirements: 1.1, 3.1, 3.2, 3.4_
  
  - [ ] 9.2 Create utils/validation.ts with validation functions
    - Implement validateSquareFootage(value) - numeric, 1-100000
    - Implement validateBedrooms(value) - integer, 0-20
    - Implement validateBathrooms(value) - numeric, 0-20, precision 0.5
    - Implement validateLocation(value) - alphanumeric + allowed chars, max 200
    - Implement validateYearBuilt(value) - integer, 1800 to current_year+1
    - Implement validateForm(formData) - returns ValidationErrors object
    - _Requirements: 1.2, 1.3, 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ] 9.3 Create utils/formatting.ts with formatting functions
    - Implement formatCurrency(value) - returns USD format with 2 decimal places
    - _Requirements: 3.1, 3.2_
  
  - [ ]* 9.4 Write property tests for frontend validation
    - **Property 1: Input Validation Range Compliance** (frontend side)
    - **Validates: Requirements 1.2, 1.3, 10.1-10.5**
    - Use fast-check to generate valid inputs within ranges
    - Verify validation functions accept valid inputs
    - Use fast-check to generate invalid inputs
    - Verify validation functions reject invalid inputs with error messages
  
  - [ ]* 9.5 Write property test for currency formatting consistency
    - **Property 6: Currency Formatting Consistency**
    - **Validates: Requirements 3.1, 3.2, 11.2, 11.3**
    - Use fast-check to generate random numeric values
    - Verify formatCurrency returns exactly 2 decimal places
    - Verify format includes $ prefix and thousands separators

- [ ] 10. Implement PredictionForm component
  - [ ] 10.1 Create components/PredictionForm.tsx
    - Initialize state: formData, errors, isSubmitting, isValid
    - Implement handleInputChange to update field and validate
    - Implement validateField to return error message or null
    - Implement validateForm to check all fields and update isValid
    - Implement handleSubmit to POST to backend /predict endpoint with axios
    - Render form with input fields for square_footage, bedrooms, bathrooms, location, year_built
    - Display clear labels and placeholder text for each field
    - Display validation error messages below each field
    - Disable submit button when isValid is false or isSubmitting is true
    - Set 30-second timeout on axios request
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.7_
  
  - [ ]* 10.2 Write property test for valid input enables submission
    - **Property 2: Valid Input Enables Submission**
    - **Validates: Requirements 1.4**
    - Use fast-check to generate form states with all valid fields
    - Verify submit button is enabled
    - Generate form states with missing or invalid fields
    - Verify submit button is disabled
  
  - [ ]* 10.3 Write property test for prediction request data integrity
    - **Property 3: Prediction Request Data Integrity**
    - **Validates: Requirements 2.1**
    - Use fast-check to generate valid property details
    - Mock axios POST request
    - Verify request payload contains all fields with exact values preserved

- [ ] 11. Implement PredictionResult component
  - [ ] 11.1 Create components/PredictionResult.tsx
    - Accept props: prediction (PredictionResult | null), loading (boolean), error (ErrorObject | null)
    - Display loading spinner when loading is true (show within 100ms)
    - Display predicted price formatted as USD currency using formatCurrency
    - Display confidence interval with lower_bound and upper_bound formatted as USD
    - Display error message when error is not null
    - Hide loading indicator when loading becomes false
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 11.2 Write unit tests for prediction result display
    - Test loading spinner displays when loading=true
    - Test prediction displays with correct currency formatting
    - Test confidence metrics display with bounds
    - Test error displays when error is not null

- [ ] 12. Implement ErrorDisplay component
  - [ ] 12.1 Create components/ErrorDisplay.tsx
    - Accept props: error (ErrorObject), onRetry (optional callback)
    - Display error icon
    - Display error type label (network/validation/server/timeout)
    - Display error message from error.message
    - Display retry button if onRetry provided
    - _Requirements: 3.4, 9.1, 9.2_
  
  - [ ]* 12.2 Write property test for error display completeness
    - **Property 7: Error Display Completeness**
    - **Validates: Requirements 3.4, 9.2, 9.6**
    - Generate ErrorObject instances with different types and messages
    - Verify component displays error type and message
    - Verify retry button appears when onRetry callback provided

- [ ] 13. Implement error state management
  - [ ] 13.1 Update PredictionForm to handle errors and clear state
    - Parse error responses from backend (400, 500, 503)
    - Map HTTP status codes to error types (network, validation, server)
    - Extract error message from response "error" field
    - Clear previous error messages when new request submitted
    - Handle timeout errors (30 seconds)
    - Handle network errors (connection failure)
    - _Requirements: 2.7, 3.4, 9.1, 9.2, 9.5, 9.6, 9.7_
  
  - [ ]* 13.2 Write property test for error state clearing
    - **Property 8: Error State Clearing**
    - **Validates: Requirements 9.5**
    - Simulate sequence of requests with errors followed by new request
    - Verify previous error messages cleared before displaying new results

- [ ] 14. Implement ModelInfo component
  - [ ] 14.1 Create components/ModelInfo.tsx
    - Display dataset description with feature names (square footage, bedrooms, bathrooms, location, year built) and target variable (price)
    - Display preprocessing steps as list or paragraph
    - Display model type as "Linear Regression"
    - Display model metrics (RMSE with units, R² score as decimal 0-1)
    - Handle loading state with loading indicator
    - Handle error state with error message
    - _Requirements: 4.3, 4.4, 4.5, 4.6, 4.7_
  
  - [ ]* 14.2 Write unit tests for ModelInfo component
    - Test dataset description displays feature names
    - Test preprocessing steps display
    - Test model metrics display with correct formatting
    - Test error message displays when data fails to load

- [ ] 15. Implement routing and navigation
  - [ ] 15.1 Create App.tsx with routing
    - Set up React Router with routes: "/" (home with prediction form), "/about" (model info page)
    - Create navigation header with logo/title and "About"/"Model Info" link
    - Implement navigation link click to navigate within 500ms
    - _Requirements: 4.1, 4.2_
  
  - [ ]* 15.2 Write integration tests for navigation
    - Test clicking "About" link navigates to model info page
    - Test navigation completes within 500ms
    - Test all routes render without errors

- [ ] 16. Checkpoint - Verify frontend core functionality
  - Run all frontend unit tests (npm test)
  - Manually test form validation with valid/invalid inputs
  - Manually test form submission (can mock backend)
  - Manually test navigation between pages
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Implement responsive design
  - [ ] 17.1 Create responsive CSS styles
    - Set up media queries for mobile (<768px) and desktop (≥768px)
    - Implement vertical stacking of form elements on mobile
    - Implement multi-column layout on desktop
    - Ensure no horizontal scrolling from 320px to 1920px
    - Use responsive typography (14px-24px) scaling with viewport
    - Ensure touch targets minimum 44x44px on mobile
    - Ensure all navigation and actions visible at all widths
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_
  
  - [ ]* 17.2 Write responsive design tests
    - Test layout at breakpoints: 320px, 768px, 1024px, 1920px
    - Verify no horizontal scrolling at all widths
    - Verify vertical stacking on mobile
    - Verify multi-column layout on desktop
    - Verify touch target sizes on mobile

- [ ] 18. Implement UI aesthetics and styling
  - [ ] 18.1 Apply professional design system
    - Define color palette: max 5 colors from blues (#2C3E50, #3498DB), grays (#ECF0F1, #95A5A6), earth tones (#8B7355, #D2B48C)
    - Ensure text contrast ratios meet WCAG AA (4.5:1 normal text, 3.0:1 large text)
    - Use consistent spacing multiples of 4px/8px with max 10 distinct values
    - Use max 3 font families, max 6 font sizes, max 4 font weights
    - Style navigation header with logo/title (min 40px height)
    - Apply consistent styling to buttons, inputs, cards across all pages
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_
  
  - [ ]* 18.2 Write accessibility and visual consistency tests
    - Use axe-core to verify WCAG AA contrast ratios
    - Verify color palette limited to 5 colors
    - Verify spacing uses consistent values
    - Verify typography uses max 3 font families

- [ ] 19. Implement backend Dockerfile and deployment configuration
  - [ ] 19.1 Create backend/Dockerfile
    - Use Python 3.9+ base image
    - Copy requirements.txt and install dependencies
    - Copy application code
    - Set working directory
    - Expose port (read from PORT env variable, default 8000)
    - Set CMD to run uvicorn with main:app
    - _Requirements: 12.5_
  
  - [ ] 19.2 Create docker-compose.yml
    - Define backend service with build context, environment variables (MODEL_PATH, PORT, CORS_ALLOWED_ORIGINS), volume mount for model file, port mapping
    - Define frontend service with build context, environment variables (REACT_APP_API_URL), port mapping, depends_on backend
    - Set up network for service communication
    - _Requirements: 12.9_

- [ ] 20. Implement frontend Dockerfile
  - [ ] 20.1 Create frontend/Dockerfile
    - Use Node 16+ base image
    - Copy package.json and install dependencies
    - Copy application code
    - Set REACT_APP_API_URL build argument
    - Run build command (fail if REACT_APP_API_URL not set)
    - Use nginx or serve to serve static build files
    - Expose port 3000
    - _Requirements: 12.6_

- [ ] 21. Create documentation
  - [ ] 21.1 Create README.md
    - Document system overview and architecture
    - Document required environment variables: MODEL_PATH (backend model file path), PORT (backend port, default 8000), REACT_APP_API_URL (frontend API URL), CORS_ALLOWED_ORIGINS (allowed frontend origins)
    - Provide example values for each environment variable
    - Document installation steps (clone, install dependencies)
    - Document how to run locally (backend, frontend separately)
    - Document how to run with Docker (docker-compose up)
    - Document API endpoints (/predict POST, /health GET)
    - Document testing commands (pytest, npm test)
    - _Requirements: 12.4_

- [ ] 22. Final integration and testing
  - [ ]* 22.1 Write end-to-end integration tests
    - Test complete prediction flow: input → submit → backend → model → response → display
    - Test health check endpoint availability
    - Test CORS headers present in responses
    - Test error propagation from backend to frontend
  
  - [ ] 22.2 Test Docker deployment
    - Build backend Docker image successfully
    - Build frontend Docker image successfully
    - Run docker-compose and verify services start
    - Test prediction request through dockerized services
    - Verify environment variables configure services correctly
  
  - [ ] 22.3 Manual testing checklist
    - Test prediction with valid property details
    - Test prediction with missing fields (verify 400 error)
    - Test prediction with out-of-range values (verify 400 error)
    - Test timeout scenario (verify timeout message after 30 seconds)
    - Test network error scenario (stop backend, verify network error message)
    - Test responsive design at multiple screen sizes
    - Test navigation between home and about pages
    - Test model info page displays correctly

- [ ] 23. Final checkpoint - Complete system verification
  - Run all tests (backend pytest, frontend Jest)
  - Verify Docker images build successfully
  - Verify docker-compose orchestrates services correctly
  - Verify README documentation is complete and accurate
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation of functionality
- Property-based tests validate universal correctness properties across randomized inputs
- Unit tests validate specific examples, edge cases, and component behavior
- The backend uses Python with FastAPI, Pydantic, scikit-learn, hypothesis
- The frontend uses React with TypeScript, axios, fast-check
- Testing libraries: pytest and hypothesis (backend), Jest and fast-check (frontend)
- Early tasks establish infrastructure; middle tasks implement core logic; later tasks add polish and deployment
- Each property test is annotated with the property number and requirements it validates

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1", "8.1"] },
    { "id": 1, "tasks": ["2.1", "9.1"] },
    { "id": 2, "tasks": ["2.2", "3.1", "9.2", "9.3"] },
    { "id": 3, "tasks": ["3.2", "3.3", "4.1", "9.4", "9.5"] },
    { "id": 4, "tasks": ["4.2", "5.1"] },
    { "id": 5, "tasks": ["5.2", "5.3", "5.4", "6.1", "10.1"] },
    { "id": 6, "tasks": ["6.2", "6.3", "10.2", "10.3", "11.1"] },
    { "id": 7, "tasks": ["11.2", "12.1"] },
    { "id": 8, "tasks": ["12.2", "13.1", "14.1"] },
    { "id": 9, "tasks": ["13.2", "14.2", "15.1"] },
    { "id": 10, "tasks": ["15.2", "17.1"] },
    { "id": 11, "tasks": ["17.2", "18.1"] },
    { "id": 12, "tasks": ["18.2", "19.1", "20.1"] },
    { "id": 13, "tasks": ["19.2", "21.1"] },
    { "id": 14, "tasks": ["22.1", "22.2", "22.3"] }
  ]
}
```
