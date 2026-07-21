from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.modules.swaps.repository import SwapRepository, SwapWithMeal
from app.modules.swaps.schemas import CreateSwapRequest, SwapActionRequest, SwapHistoryResponse, SwapMealResponse, SwapResponse, SwapRole


class SwapService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = SwapRepository(session)

    async def create(self, *, requester_id: UUID, request: CreateSwapRequest) -> SwapResponse:
        meal = await self.repository.get_available_meal(request.meal_id)
        if meal is None:
            raise NotFoundError("Available meal not found")
        if meal.owner_id == requester_id:
            raise BadRequestError("You cannot request a swap for your own meal")
        if await self.repository.has_pending_request(requester_id=requester_id, meal_id=meal.id):
            raise ConflictError("You already have a pending request for this meal")
        try:
            swap = await self.repository.create_request(
                meal_id=meal.id, requester_id=requester_id, recipient_id=meal.owner_id, message=request.message
            )
        except ValueError as exc:
            if str(exc) == "duplicate_pending_request":
                raise ConflictError("You already have a pending request for this meal") from exc
            raise
        record = await self.repository.get_with_meal(swap.id)
        if record is None:  # Defensive guard; the swap was just persisted.
            raise NotFoundError("Swap request not found")
        return await self._to_response(record)

    async def list(self, *, user_id: UUID, role: SwapRole, status: str | None) -> list[SwapResponse]:
        records = await self.repository.list_for_user(user_id=user_id, role=role, status=status)
        return [await self._to_response(record) for record in records]

    async def accept(self, *, user_id: UUID, swap_id: UUID, request: SwapActionRequest) -> SwapResponse:
        return await self._transition(
            user_id=user_id, swap_id=swap_id, request=request,
            expected_status="pending", next_status="accepted", action="ACCEPTED",
            recipient_only=True, reserve_meal=True,
        )

    async def reject(self, *, user_id: UUID, swap_id: UUID, request: SwapActionRequest) -> SwapResponse:
        return await self._transition(
            user_id=user_id, swap_id=swap_id, request=request,
            expected_status="pending", next_status="rejected", action="REJECTED",
            recipient_only=True, reserve_meal=False,
        )

    async def cancel(self, *, user_id: UUID, swap_id: UUID, request: SwapActionRequest) -> SwapResponse:
        record = await self.repository.get_with_meal(swap_id)
        if record is None:
            raise NotFoundError("Swap request not found")
        swap = record.swap
        if swap.requester_id != user_id:
            raise ForbiddenError("Only the requester can cancel this swap")
        return await self._transition(
            user_id=user_id, swap_id=swap_id, request=request,
            expected_status="pending", next_status="rejected", action="CANCELLED",
            recipient_only=False, reserve_meal=False,
        )

    async def complete(self, *, user_id: UUID, swap_id: UUID, request: SwapActionRequest) -> SwapResponse:
        return await self._transition(
            user_id=user_id, swap_id=swap_id, request=request,
            expected_status="accepted", next_status="completed", action="COMPLETED",
            recipient_only=False, reserve_meal=False,
        )

    async def _transition(
        self, *, user_id: UUID, swap_id: UUID, request: SwapActionRequest, expected_status: str,
        next_status: str, action: str, recipient_only: bool, reserve_meal: bool,
    ) -> SwapResponse:
        record = await self.repository.get_with_meal(swap_id)
        if record is None:
            raise NotFoundError("Swap request not found")
        swap = record.swap
        if recipient_only and swap.recipient_id != user_id:
            raise ForbiddenError("Only the meal owner can perform this action")
        if not recipient_only and user_id not in {swap.requester_id, swap.recipient_id}:
            raise ForbiddenError("Only a swap participant can complete this request")
        if swap.status != expected_status:
            raise BadRequestError(f"Only {expected_status} swaps can be marked {next_status}")
        updated = await self.repository.transition(
            swap_id=swap_id, expected_status=expected_status, next_status=next_status, action=action,
            actor_id=user_id, details={"note": request.note} if request.note else {}, reserve_meal=reserve_meal,
        )
        if updated is None:
            raise BadRequestError("This swap was updated by another request; refresh and try again")
        updated_record = await self.repository.get_with_meal(updated.id)
        if updated_record is None:
            raise NotFoundError("Swap request not found")
        return await self._to_response(updated_record)

    async def _to_response(self, record: SwapWithMeal) -> SwapResponse:
        history = await self.repository.list_history(record.swap.id)
        return SwapResponse(
            id=record.swap.id, meal_id=record.swap.meal_id, requester_id=record.swap.requester_id,
            recipient_id=record.swap.recipient_id, message=record.swap.message, status=record.swap.status,
            meal=SwapMealResponse(id=record.swap.meal_id, title=record.meal_title, image_url=record.meal_image_url),
            history=[SwapHistoryResponse.model_validate(event) for event in history],
            created_at=record.swap.created_at, updated_at=record.swap.updated_at,
        )
