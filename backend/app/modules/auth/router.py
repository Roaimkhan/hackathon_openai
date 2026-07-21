from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import success_payload
from app.core.security import get_token_subject
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    return AuthService(session)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, service: AuthService = Depends(get_auth_service)):
    user, token = await service.register(request)
    payload = TokenResponse(access_token=token, user=UserResponse.model_validate(user))
    return success_payload(payload.model_dump(mode="json"))


@router.post("/login")
async def login(request: LoginRequest, service: AuthService = Depends(get_auth_service)):
    user, token = await service.login(request)
    payload = TokenResponse(access_token=token, user=UserResponse.model_validate(user))
    return success_payload(payload.model_dump(mode="json"))


@router.get("/me")
async def get_me(
    user_id: UUID = Depends(get_token_subject), service: AuthService = Depends(get_auth_service)
):
    user = await service.current_user(user_id)
    return success_payload(UserResponse.model_validate(user).model_dump(mode="json"))
