from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User


class UserRepository:
    """Persistence-only operations for the users table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email.lower())
        return await self.session.scalar(statement)

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def create(self, *, email: str, display_name: str, password_hash: str) -> User:
        user = User(email=email.lower(), display_name=display_name, password_hash=password_hash)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
