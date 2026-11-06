from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserRead

# Create a router instance for user-related endpoints
router = APIRouter()

# Define an endpoint to retrieve the current authenticated user's information
@router.get(
    "/me",
    response_model=UserRead,
)
# Use dependency injection to get the current authenticated user
def get_me(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):

    return current_user