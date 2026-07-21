from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository
from app.modules.auth.schemas import LoginRequest, RegisterRequest
from app.modules.profiles.repository import ProfileRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)
        self.profiles = ProfileRepository(session)

    async def register(self, request: RegisterRequest) -> tuple[User, str]:
        if await self.users.get_by_email(request.email):
            raise ConflictError("An account with this email already exists")
        user = await self.users.create(
            email=str(request.email),
            display_name=request.display_name.strip(),
            password_hash=hash_password(request.password),
        )
        await self.profiles.create_defaults(
            user_id=user.id, latitude=request.latitude, longitude=request.longitude
        )
        return user, create_access_token(user.id)

    async def login(self, request: LoginRequest) -> tuple[User, str]:
        user = await self.users.get_by_email(str(request.email))
        if user is None or not verify_password(request.password, user.password_hash):
            raise AuthenticationError("Invalid email or password")
        return user, create_access_token(user.id)

    async def current_user(self, user_id: UUID) -> User:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user
