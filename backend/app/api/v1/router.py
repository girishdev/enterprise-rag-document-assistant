from fastapi import APIRouter

from app.api.v1.routers import (
    auth,
    chat,
    conversations,
    health,
    users,
    documents,
)

# Create an API router instance to manage all the routes for version 1 of the API
api_router = APIRouter()

# Include the health check router with a prefix and tag for organization
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)

# Include the authentication router with a prefix and tag for organization
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# Include the chat router with a prefix and tag for organization
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"],
)

# Include the conversations router with a prefix and tag for organization
api_router.include_router(
    conversations.router,
    prefix="/conversations",
    tags=["Conversations"],
)

# Include the users router with a prefix and tag for organization
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

# Include the documents router with a prefix and tag for organization
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
)