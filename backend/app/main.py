from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.api.v1.routers import retrieval


# Load application settings from the configuration
settings = get_settings()

# FastAPI application instance
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)

# Include the API router with a prefix
app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)

# Add CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a root endpoint that returns a welcome message
@app.get("/")
def root():
    return {
        "message": "Enterprise RAG Document Assistant API"
    }

app.include_router(
    retrieval.router,
    prefix="/api/v1",
)