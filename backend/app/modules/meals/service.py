from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.modules.ai.service import AIService
from app.modules.meals.models import Meal
from app.modules.meals.repository import MealRepository
from app.modules.meals.schemas import MealDraftCreate, MealImageResponse, MealResponse
from app.modules.profiles.repository import ProfileRepository
from app.modules.storage.service import StorageService


class MealService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = MealRepository(session)
        self.profiles = ProfileRepository(session)
        self.storage = StorageService()
        self.ai = AIService()

    async def create_draft(self, owner_id: UUID, request: MealDraftCreate) -> MealResponse:
        profile = await self.profiles.get_profile(owner_id)
        meal = await self.repository.create(
            owner_id=owner_id,
            title=(request.title or "Homemade meal").strip(),
            description=(request.description or "Freshly prepared homemade food.").strip(),
            location=request.location.strip() if request.location else None,
            latitude=request.latitude if request.latitude is not None else (profile.latitude if profile else None),
            longitude=request.longitude if request.longitude is not None else (profile.longitude if profile else None),
        )
        return await self._to_response(meal)

    async def get_meal(self, meal_id: UUID) -> MealResponse:
        meal = await self.repository.get_by_id(meal_id)
        if meal is None:
            raise NotFoundError("Meal not found")
        return await self._to_response(meal)

    async def list_mine(self, owner_id: UUID) -> list[MealResponse]:
        return [await self._to_response(meal) for meal in await self.repository.list_by_owner(owner_id)]

    async def remove(self, owner_id: UUID, meal_id: UUID) -> MealResponse:
        meal = await self.repository.get_by_id(meal_id)
        if meal is None:
            raise NotFoundError("Meal not found")
        if meal.owner_id != owner_id:
            raise ForbiddenError("Only the meal owner can remove this listing")
        updated = await self.repository.mark_unavailable(meal_id=meal_id, owner_id=owner_id)
        if updated is None:
            raise NotFoundError("Meal not found")
        return await self._to_response(updated)

    async def upload_image(self, *, owner_id: UUID, meal_id: UUID, filename: str, content_type: str, content: bytes) -> MealResponse:
        meal = await self.repository.get_by_id(meal_id)
        if meal is None:
            raise NotFoundError("Meal not found")
        if meal.owner_id != owner_id:
            raise ForbiddenError("Only the meal owner can add an image")

        upload = await self.storage.upload_meal_image(
            meal_id=meal_id, filename=filename, content_type=content_type, content=content
        )
        images = await self.repository.list_images(meal_id)
        await self.repository.add_image(
            meal_id=meal_id,
            public_url=upload.image_url,
            storage_path=upload.storage_path,
            position=len(images),
        )
        analysis = await self.ai.analyze_meal(
            image_url=upload.image_url, title_hint=meal.title, description_hint=meal.description
        )
        if analysis is not None:
            meal = await self.repository.update_analysis(meal, **analysis.model_dump(), status="complete")
        # If GPT is unavailable/invalid, the original user draft remains usable and stays pending.
        return await self._to_response(meal)

    async def _to_response(self, meal: Meal) -> MealResponse:
        images = await self.repository.list_images(meal.id)
        return MealResponse(
            id=meal.id, owner_id=meal.owner_id, title=meal.title, description=meal.description,
            cuisine=meal.cuisine, spice_level=meal.spice_level, dietary_tags=meal.dietary_tags,
            allergens=meal.allergens, taste_notes=meal.taste_notes, analysis_status=meal.analysis_status,
            location=meal.location,
            latitude=meal.latitude, longitude=meal.longitude,
            images=[MealImageResponse.model_validate(image) for image in images],
            created_at=meal.created_at, updated_at=meal.updated_at,
        )
