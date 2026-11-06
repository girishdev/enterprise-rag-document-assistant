from fastapi import APIRouter

# Create a router instance for health check endpoints
router = APIRouter()

# Define a health check endpoint that returns the status of the application
@router.get("")
def health():
    return {
        "status": "ok"
    }