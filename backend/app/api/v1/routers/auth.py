from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService

# Create a router instance for authentication-related endpoints
router = APIRouter()

# Define an endpoint to register a new user
@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
# Use dependency injection to get the database session
def register(
    data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
):

    # Create an instance of the AuthService to handle authentication logic
    service = AuthService(db)

    # Try to register the new user using the provided data
    try:
        # If the email is already registered, a ValueError will be raised
        return service.register(data)

    except ValueError:
        # If a ValueError is raised, it means the email is already registered, so we raise an HTTP 409 Conflict exception
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

# Define an endpoint to log in a user and return an access token
@router.post(
    "/login",
    response_model=Token,
)
# Use dependency injection to get the form data and database session
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    # Create an instance of the AuthService to handle authentication logic
    service = AuthService(db)

    # Authenticate the user using the provided email and password
    user = service.authenticate(
        form_data.username,
        form_data.password,
    )

    # If the user is not found or the credentials are invalid, raise an HTTP 401 Unauthorized exception
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    # Create an access token for the authenticated user using their user ID
    token = create_access_token(
        str(user.id)
    )

    # Return the access token in the response
    return Token(
        access_token=token
    )