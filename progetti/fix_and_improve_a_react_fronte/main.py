# Task: Fix and Improve a React Frontend Connected to Python FastAPI APIs

import logging
import traceback
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# ==========================================
# 1. LOGGING CONFIGURATION (For Debugging)
# ==========================================
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api_debug.log")
    ]
)
logger = logging.getLogger("fastapi_react_backend")

# ==========================================
# 2. APP INITIALIZATION & CORS (For React)
# ==========================================
app = FastAPI(
    title="React-FastAPI Backend",
    description="API with advanced debugging and CORS configured for React frontend.",
    version="1.0.0"
)

# Crucial for React Frontend to communicate with FastAPI without CORS errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 3. GLOBAL EXCEPTION HANDLER (For Debugging)
# ==========================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches all unhandled exceptions, logs the full traceback for Python debugging,
    and returns a structured JSON response to the React frontend.
    """
    error_msg = f"Unhandled error on {request.method} {request.url.path}"
    logger.error(f"{error_msg}: {str(exc)}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": request.url.path
        }
    )

# ==========================================
# 4. PYDANTIC MODELS (Data Validation)
# ==========================================
class UserData(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    is_active: bool = True

class ErrorResponse(BaseModel):
    detail: str

# ==========================================
# 5. API ENDPOINTS
# ==========================================
@app.get("/api/health", tags=["System"])
async def health_check():
    """Simple health check endpoint for the frontend to verify connection."""
    logger.debug("Health check endpoint called by frontend.")
    return {"status": "ok", "message": "FastAPI backend is running smoothly."}

@app.get("/api/users", response_model=List[UserData], tags=["Users"])
async def get_users():
    """Simulates fetching users from a database."""
    logger.debug("Fetching user list for frontend.")
