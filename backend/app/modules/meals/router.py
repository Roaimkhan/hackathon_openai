from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import success_payload
from app.core.security import get_token_subject
from app.modules.meals.schemas import MealCreate
from app.modules.meals.service import MealService

router = APIRouter(prefix="/meals", tags=["meals"])


def get_meal_service(session: AsyncSession = Depends(get_db_session)) -> MealService:
    return MealService(session)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_meal(
    request: MealCreate,
    user_id: UUID = Depends(get_token_subject),
    service: MealService = Depends(get_meal_service),
):
    return success_payload((await service.create_draft(user_id, request)).model_dump(mode="json"))


@router.get("/mine")
async def list_my_meals(user_id: UUID = Depends(get_token_subject), service: MealService = Depends(get_meal_service)):
    meals = await service.list_mine(user_id)
    return success_payload([meal.model_dump(mode="json") for meal in meals], {"count": len(meals)})


@router.get("/{meal_id}")
async def get_meal(meal_id: UUID, service: MealService = Depends(get_meal_service)):
    return success_payload((await service.get_meal(meal_id)).model_dump(mode="json"))


@router.post("/{meal_id}/image-upload")
async def upload_meal_image(
    meal_id: UUID,
    image: UploadFile = File(...),
    user_id: UUID = Depends(get_token_subject),
    service: MealService = Depends(get_meal_service),
):
    content = await image.read()
    meal = await service.upload_image(
        owner_id=user_id,
        meal_id=meal_id,
        filename=image.filename or "meal-image",
        content_type=image.content_type or "",
        content=content,
    )
    return success_payload(meal.model_dump(mode="json"))


@router.delete("/{meal_id}")
async def delete_meal(
    meal_id: UUID,
    user_id: UUID = Depends(get_token_subject),
    service: MealService = Depends(get_meal_service),
):
    meal = await service.remove(owner_id=user_id, meal_id=meal_id)
    return success_payload(meal.model_dump(mode="json"))
