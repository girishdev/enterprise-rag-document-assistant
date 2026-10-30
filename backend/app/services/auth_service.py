from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def register(
        self,
        data: UserCreate,
    ) -> User:

        email = str(data.email).lower()

        existing_user = self.repository.get_by_email(email)

        if existing_user:
            raise ValueError("EMAIL_EXISTS")

        user = User(
            email=email,
            full_name=data.full_name,
            hashed_password=hash_password(
                data.password
            ),
        )

        return self.repository.create(user)

    def authenticate(
        self,
        email: str,
        password: str,
    ) -> User | None:

        user = self.repository.get_by_email(
            email.lower()
        )

        if user is None:
            return None

        if not verify_password(
            password,
            user.hashed_password,
        ):
            return None

        return user