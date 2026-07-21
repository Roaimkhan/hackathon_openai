from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.profiles.models import Profile, TasteProfile


class ProfileRepository:
    """Persistence-only access to saved user location and preferences."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_defaults(self, *, user_id: UUID, latitude: float | None, longitude: float | None) -> None:
        self.session.add(Profile(user_id=user_id, latitude=latitude, longitude=longitude))
        self.session.add(TasteProfile(user_id=user_id))
        await self.session.commit()

    async def get_profile(self, user_id: UUID) -> Profile | None:
        return await self.session.get(Profile, user_id)

    async def get_taste_profile(self, user_id: UUID) -> TasteProfile | None:
        return await self.session.get(TasteProfile, user_id)
