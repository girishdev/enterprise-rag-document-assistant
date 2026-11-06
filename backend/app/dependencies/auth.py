from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

# Load application settings from the configuration
settings = get_settings()

# Define an OAuth2 password bearer instance for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)

# Define a dependency function to get the current authenticated user based on the provided token
def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> User:

    try:
        # Decode the JWT token using the secret key and algorithm specified in the settings
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        # Extract the user ID from the token payload and convert it to a UUID
        user_id = UUID(
            payload["sub"]
        )

    except (
        InvalidTokenError,
        KeyError,
        ValueError,
    ):
        # If the token is invalid or the user ID cannot be extracted, raise an HTTP 401 Unauthorized exception
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    # Create an instance of the UserRepository to interact with the user data in the database
    repository = UserRepository(db)

    # Retrieve the user from the database using the user ID extracted from the token
    user = repository.get_by_id(user_id)

    # If the user is not found, raise an HTTP 401 Unauthorized exception
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user