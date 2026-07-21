from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import and_, func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.schemas import SearchIntentResult
from app.modules.auth.models import User
from app.modules.meals.models import Meal, MealImage


@dataclass(frozen=True)
class MealCandidate:
    meal: Meal
    image_url: str
    owner_name: str
    latitude: float | None
    longitude: float | None
    distance_km: float


class SearchRepository:
    """PostgreSQL candidate selection, filtering, and great-circle distance calculation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def nearby_candidates(
        self,
        *,
        viewer_id: UUID,
        latitude: float | None,
        longitude: float | None,
        radius_km: float | None = None,
        intent: SearchIntentResult | None = None,
        limit: int = 12,
    ) -> list[MealCandidate]:
        if latitude is not None and longitude is not None:
            distance_km = (
                6371.0
                * func.acos(
                    func.least(
                        1.0,
                        func.greatest(
                            -1.0,
                            func.cos(func.radians(latitude))
                            * func.cos(func.radians(Meal.latitude))
                            * func.cos(func.radians(Meal.longitude) - func.radians(longitude))
                            + func.sin(func.radians(latitude)) * func.sin(func.radians(Meal.latitude)),
                        ),
                    )
                )
            ).label("distance_km")
            statement = (
                select(Meal, MealImage.public_url, User.display_name, Meal.latitude, Meal.longitude, distance_km)
                .join(MealImage, and_(MealImage.meal_id == Meal.id, MealImage.position == 0))
                .join(User, User.id == Meal.owner_id)
                .where(
                    Meal.owner_id != viewer_id,
                    Meal.is_available.is_(True),
                    Meal.latitude.is_not(None),
                    Meal.longitude.is_not(None),
                )
            )
            if radius_km is not None:
                statement = statement.where(distance_km <= radius_km)
            statement = statement.order_by(distance_km.asc()).limit(limit)
        else:
            distance_km = literal_column("0.0").label("distance_km")
            statement = (
                select(Meal, MealImage.public_url, User.display_name, Meal.latitude, Meal.longitude, distance_km)
                .join(MealImage, and_(MealImage.meal_id == Meal.id, MealImage.position == 0))
                .join(User, User.id == Meal.owner_id)
                .where(
                    Meal.owner_id != viewer_id,
                    Meal.is_available.is_(True),
                )
                .limit(limit)
            )
        if intent and intent.cuisine:
            statement = statement.where(func.lower(Meal.cuisine) == intent.cuisine.lower())
        if intent and intent.max_spice_level is not None:
            statement = statement.where(Meal.spice_level <= intent.max_spice_level)
        if intent and intent.tags:
            statement = statement.where(Meal.dietary_tags.contains(intent.tags))
        rows = (await self.session.execute(statement)).all()
        return [MealCandidate(meal=row[0], image_url=row[1], owner_name=row[2], latitude=row[3], longitude=row[4], distance_km=float(row[5])) for row in rows]
