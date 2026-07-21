from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from sqlalchemy import and_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.meals.models import Meal, MealImage
from app.modules.swaps.models import SwapHistory, SwapRequest


@dataclass(frozen=True)
class SwapWithMeal:
    swap: SwapRequest
    meal_title: str
    meal_image_url: str | None


class SwapRepository:
    """Persistence-only swap, history, and target-meal operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_available_meal(self, meal_id: UUID) -> Meal | None:
        statement = select(Meal).where(Meal.id == meal_id, Meal.is_available.is_(True))
        return await self.session.scalar(statement)

    async def has_pending_request(self, *, requester_id: UUID, meal_id: UUID) -> bool:
        statement = select(SwapRequest.id).where(
            SwapRequest.requester_id == requester_id,
            SwapRequest.meal_id == meal_id,
            SwapRequest.status == "pending",
        )
        return (await self.session.scalar(statement)) is not None

    async def create_request(
        self, *, meal_id: UUID, requester_id: UUID, recipient_id: UUID, message: str | None
    ) -> SwapRequest:
        try:
            swap = SwapRequest(
                meal_id=meal_id,
                requester_id=requester_id,
                recipient_id=recipient_id,
                message=message,
                status="pending",
            )
            self.session.add(swap)
            await self.session.flush()
            self.session.add(
                SwapHistory(
                    swap_request_id=swap.id,
                    action="CREATED",
                    actor_id=requester_id,
                    details={"message": message} if message else {},
                )
            )
            await self.session.commit()
            await self.session.refresh(swap)
            return swap
        except IntegrityError as exc:
            await self.session.rollback()
            raise ValueError("duplicate_pending_request") from exc

    async def get_with_meal(self, swap_id: UUID) -> SwapWithMeal | None:
        statement = (
            select(SwapRequest, Meal.title, MealImage.public_url)
            .join(Meal, Meal.id == SwapRequest.meal_id)
            .outerjoin(MealImage, and_(MealImage.meal_id == Meal.id, MealImage.position == 0))
            .where(SwapRequest.id == swap_id)
        )
        row = (await self.session.execute(statement)).one_or_none()
        return SwapWithMeal(swap=row[0], meal_title=row[1], meal_image_url=row[2]) if row else None

    async def list_for_user(
        self, *, user_id: UUID, role: Literal["all", "sent", "received"], status: str | None
    ) -> list[SwapWithMeal]:
        statement = (
            select(SwapRequest, Meal.title, MealImage.public_url)
            .join(Meal, Meal.id == SwapRequest.meal_id)
            .outerjoin(MealImage, and_(MealImage.meal_id == Meal.id, MealImage.position == 0))
        )
        if role == "sent":
            statement = statement.where(SwapRequest.requester_id == user_id)
        elif role == "received":
            statement = statement.where(SwapRequest.recipient_id == user_id)
        else:
            statement = statement.where((SwapRequest.requester_id == user_id) | (SwapRequest.recipient_id == user_id))
        if status:
            statement = statement.where(SwapRequest.status == status)
        rows = (await self.session.execute(statement.order_by(SwapRequest.updated_at.desc()))).all()
        return [SwapWithMeal(swap=row[0], meal_title=row[1], meal_image_url=row[2]) for row in rows]

    async def list_history(self, swap_id: UUID) -> list[SwapHistory]:
        statement = select(SwapHistory).where(SwapHistory.swap_request_id == swap_id).order_by(SwapHistory.created_at.asc())
        return list(await self.session.scalars(statement))

    async def transition(
        self,
        *,
        swap_id: UUID,
        expected_status: str,
        next_status: str,
        action: str,
        actor_id: UUID,
        details: dict,
        reserve_meal: bool = False,
    ) -> SwapRequest | None:
        """Compare-and-set transition with audit entry in a single transaction."""
        try:
            if reserve_meal:
                reservation = await self.session.execute(
                    update(Meal)
                    .where(
                        Meal.id == select(SwapRequest.meal_id).where(SwapRequest.id == swap_id).scalar_subquery(),
                        Meal.is_available.is_(True),
                    )
                    .values(is_available=False)
                )
                if reservation.rowcount != 1:
                    await self.session.rollback()
                    return None
            statement = (
                update(SwapRequest)
                .where(SwapRequest.id == swap_id, SwapRequest.status == expected_status)
                .values(status=next_status)
                .returning(SwapRequest)
            )
            swap = (await self.session.execute(statement)).scalar_one_or_none()
            if swap is None:
                await self.session.rollback()
                return None
            self.session.add(SwapHistory(swap_request_id=swap.id, action=action, actor_id=actor_id, details=details))
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        await self.session.refresh(swap)
        return swap
