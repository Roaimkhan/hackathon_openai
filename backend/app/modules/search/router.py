from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import success_payload
from app.core.security import get_token_subject
from app.modules.search.service import SearchService

router = APIRouter(tags=["feed", "search"])


def get_search_service(session: AsyncSession = Depends(get_db_session)) -> SearchService:
    return SearchService(session)


@router.get("/feed")
async def get_feed(
    latitude: float | None = Query(default=None, ge=-90, le=90),
    longitude: float | None = Query(default=None, ge=-180, le=180),
    radius_km: float = Query(default=10.0, gt=0, le=100),
    limit: int = Query(default=12, ge=1, le=20),
    user_id: UUID = Depends(get_token_subject),
    service: SearchService = Depends(get_search_service),
):
    data = await service.feed(
        viewer_id=user_id, latitude=latitude, longitude=longitude, radius_km=radius_km, limit=limit
    )
    return success_payload(data, {"radius_km": radius_km})


@router.get("/search")
async def search_meals(
    q: str = Query(min_length=2, max_length=300),
    latitude: float | None = Query(default=None, ge=-90, le=90),
    longitude: float | None = Query(default=None, ge=-180, le=180),
    radius_km: float | None = Query(default=None, gt=0, le=100),
    limit: int = Query(default=12, ge=1, le=20),
    user_id: UUID = Depends(get_token_subject),
    service: SearchService = Depends(get_search_service),
):
    data, intent = await service.search_meals(
        viewer_id=user_id, query=q, latitude=latitude, longitude=longitude,
        radius_km=radius_km, limit=limit,
    )
    return success_payload(data, {"applied_filters": intent.model_dump(), "radius_km": radius_km or intent.radius_km or 10.0})
