from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import success_payload
from app.core.security import get_token_subject
from app.modules.swaps.schemas import CreateSwapRequest, SwapActionRequest, SwapRole, SwapStatus
from app.modules.swaps.service import SwapService

router = APIRouter(prefix="/swaps", tags=["swaps"])


def get_swap_service(session: AsyncSession = Depends(get_db_session)) -> SwapService:
    return SwapService(session)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_swap(
    request: CreateSwapRequest,
    user_id: UUID = Depends(get_token_subject),
    service: SwapService = Depends(get_swap_service),
):
    return success_payload((await service.create(requester_id=user_id, request=request)).model_dump(mode="json"))


@router.get("")
async def list_swaps(
    role: SwapRole = Query(default="all"),
    status_filter: SwapStatus | None = Query(default=None, alias="status"),
    user_id: UUID = Depends(get_token_subject),
    service: SwapService = Depends(get_swap_service),
):
    swaps = await service.list(user_id=user_id, role=role, status=status_filter)
    return success_payload([swap.model_dump(mode="json") for swap in swaps], {"count": len(swaps), "role": role})


@router.post("/{swap_id}/accept")
async def accept_swap(
    swap_id: UUID, request: SwapActionRequest,
    user_id: UUID = Depends(get_token_subject), service: SwapService = Depends(get_swap_service),
):
    return success_payload((await service.accept(user_id=user_id, swap_id=swap_id, request=request)).model_dump(mode="json"))


@router.post("/{swap_id}/reject")
async def reject_swap(
    swap_id: UUID, request: SwapActionRequest,
    user_id: UUID = Depends(get_token_subject), service: SwapService = Depends(get_swap_service),
):
    return success_payload((await service.reject(user_id=user_id, swap_id=swap_id, request=request)).model_dump(mode="json"))


@router.post("/{swap_id}/cancel")
async def cancel_swap(
    swap_id: UUID, request: SwapActionRequest,
    user_id: UUID = Depends(get_token_subject), service: SwapService = Depends(get_swap_service),
):
    return success_payload((await service.cancel(user_id=user_id, swap_id=swap_id, request=request)).model_dump(mode="json"))


@router.post("/{swap_id}/complete")
async def complete_swap(
    swap_id: UUID, request: SwapActionRequest,
    user_id: UUID = Depends(get_token_subject), service: SwapService = Depends(get_swap_service),
):
    return success_payload((await service.complete(user_id=user_id, swap_id=swap_id, request=request)).model_dump(mode="json"))
