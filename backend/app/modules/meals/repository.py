from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.meals.models import Meal, MealImage


class MealRepository:
    """Persistence-only queries for meals and their image records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, *, owner_id: UUID, title: str, description: str, location: str | None, latitude: float | None, longitude: float | None) -> Meal:
        meal = Meal(owner_id=owner_id, title=title, description=description, location=location, latitude=latitude, longitude=longitude)
        self.session.add(meal)
        await self.session.commit()
        await self.session.refresh(meal)
        return meal

    async def get_by_id(self, meal_id: UUID) -> Meal | None:
        return await self.session.get(Meal, meal_id)

    async def list_by_owner(self, owner_id: UUID) -> list[Meal]:
        result = await self.session.scalars(
            select(Meal)
            .where(Meal.owner_id == owner_id, Meal.is_available.is_(True))
            .order_by(Meal.created_at.desc())
        )
        return list(result)

    async def mark_unavailable(self, meal_id: UUID, owner_id: UUID) -> Meal | None:
        meal = await self.get_by_id(meal_id)
        if meal is None:
            return None
        if meal.owner_id != owner_id:
            return None
        meal.is_available = False
        await self.session.commit()
        await self.session.refresh(meal)
        return meal

    async def list_images(self, meal_id: UUID) -> list[MealImage]:
        result = await self.session.scalars(select(MealImage).where(MealImage.meal_id == meal_id).order_by(MealImage.position))
        return list(result)

    async def add_image(self, *, meal_id: UUID, public_url: str, storage_path: str, position: int) -> MealImage:
        image = MealImage(meal_id=meal_id, public_url=public_url, storage_path=storage_path, position=position)
        self.session.add(image)
        await self.session.commit()
        await self.session.refresh(image)
        return image

    async def update_analysis(self, meal: Meal, *, title: str, description: str, cuisine: str, spice_level: int, dietary_tags: list[str], allergens: list[str], taste_notes: list[str], status: str) -> Meal:
        meal.title = title
        meal.description = description
        meal.cuisine = cuisine
        meal.spice_level = spice_level
        meal.dietary_tags = dietary_tags
        meal.allergens = allergens
        meal.taste_notes = taste_notes
        meal.analysis_status = status
        await self.session.commit()
        await self.session.refresh(meal)
        return meal
