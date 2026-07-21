import asyncio
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.modules.ai.schemas import CompatibilityResult, SearchIntentResult
from app.modules.ai.service import AIService
from app.modules.profiles.repository import ProfileRepository
from app.modules.search.repository import MealCandidate, SearchRepository


@dataclass(frozen=True)
class Location:
    latitude: float
    longitude: float


class SearchService:
    compatibility_timeout_seconds = 2.5

    def __init__(self, session: AsyncSession) -> None:
        self.search = SearchRepository(session)
        self.profiles = ProfileRepository(session)
        self.ai = AIService()

    async def feed(
        self, *, viewer_id: UUID, latitude: float | None, longitude: float | None, radius_km: float | None, limit: int
    ) -> dict:
        location, taste_profile = await self._viewer_context(viewer_id, latitude, longitude)
        candidates = await self.search.nearby_candidates(
            viewer_id=viewer_id,
            latitude=location.latitude if location else None,
            longitude=location.longitude if location else None,
            radius_km=radius_km if location else None,
            limit=limit,
        )
        items = await self._rank(candidates, taste_profile)
        return {"items": items, "count": len(items)}

    async def search_meals(
        self, *, viewer_id: UUID, query: str, latitude: float | None, longitude: float | None,
        radius_km: float | None, limit: int,
    ) -> tuple[dict, SearchIntentResult]:
        location, taste_profile = await self._viewer_context(viewer_id, latitude, longitude)
        intent = await self.ai.parse_search_intent(query)
        effective_radius = radius_km if radius_km is not None else intent.radius_km
        candidates = await self.search.nearby_candidates(
            viewer_id=viewer_id,
            latitude=location.latitude if location else None,
            longitude=location.longitude if location else None,
            radius_km=effective_radius if location else None,
            intent=intent,
            limit=limit,
        )
        items = await self._rank(candidates, taste_profile)
        return {"items": items, "count": len(items)}, intent

    async def _viewer_context(self, viewer_id: UUID, latitude: float | None, longitude: float | None) -> tuple[Location | None, dict]:
        if (latitude is None) != (longitude is None):
            raise AppError("invalid_location", "Provide both latitude and longitude or none", 422)
        profile = await self.profiles.get_profile(viewer_id)
        taste = await self.profiles.get_taste_profile(viewer_id)
        resolved_latitude = latitude if latitude is not None else (profile.latitude if profile else None)
        resolved_longitude = longitude if longitude is not None else (profile.longitude if profile else None)
        location = None
        if resolved_latitude is not None and resolved_longitude is not None:
            location = Location(resolved_latitude, resolved_longitude)
        return location, {
            "preferences": taste.preferences if taste else [],
            "dietary_tags": taste.dietary_tags if taste else [],
        }

    async def _rank(self, candidates: list[MealCandidate], taste_profile: dict) -> list[dict]:
        async def score(candidate: MealCandidate) -> dict:
            fallback = self._fallback_score(candidate, taste_profile)
            result = await self.ai.calculate_compatibility(
                taste_profile=taste_profile,
                meal={
                    "title": candidate.meal.title,
                    "description": candidate.meal.description,
                    "cuisine": candidate.meal.cuisine,
                    "spice_level": candidate.meal.spice_level,
                    "dietary_tags": candidate.meal.dietary_tags,
                    "allergens": candidate.meal.allergens,
                    "taste_notes": candidate.meal.taste_notes,
                },
                distance_km=candidate.distance_km,
            )
            compatibility = result or fallback
            return {
                "id": str(candidate.meal.id), "owner_id": str(candidate.meal.owner_id),
                "owner_name": candidate.owner_name,
                "title": candidate.meal.title, "description": candidate.meal.description,
                "cuisine": candidate.meal.cuisine, "spice_level": candidate.meal.spice_level,
                "dietary_tags": candidate.meal.dietary_tags, "allergens": candidate.meal.allergens,
                "location": candidate.meal.location,
                "latitude": candidate.latitude, "longitude": candidate.longitude,
                "image_url": candidate.image_url, "distance_km": round(candidate.distance_km, 1),
                "compatibility_score": compatibility.score, "explanation": compatibility.explanation,
            }

        try:
            # One timeout wraps the entire concurrent batch, not each candidate serially.
            items = await asyncio.wait_for(
                asyncio.gather(*(score(candidate) for candidate in candidates)),
                timeout=self.compatibility_timeout_seconds,
            )
        except Exception:
            items = [self._fallback_item(candidate, taste_profile) for candidate in candidates]
        return sorted(items, key=lambda item: (-item["compatibility_score"], item["distance_km"]))

    @staticmethod
    def _fallback_score(candidate: MealCandidate, taste_profile: dict) -> CompatibilityResult:
        wanted_tags = {tag.lower() for tag in taste_profile.get("dietary_tags", [])}
        meal_tags = {tag.lower() for tag in candidate.meal.dietary_tags}
        dietary_bonus = 20 if wanted_tags and wanted_tags.issubset(meal_tags) else 0
        distance_score = max(0, 70 - int(candidate.distance_km * 4))
        return CompatibilityResult(
            score=min(100, distance_score + dietary_bonus),
            explanation="Match based on proximity and dietary preferences.",
        )

    def _fallback_item(self, candidate: MealCandidate, taste_profile: dict) -> dict:
        compatibility = self._fallback_score(candidate, taste_profile)
        return {
            "id": str(candidate.meal.id), "owner_id": str(candidate.meal.owner_id),
            "owner_name": candidate.owner_name,
            "title": candidate.meal.title, "description": candidate.meal.description,
            "cuisine": candidate.meal.cuisine, "spice_level": candidate.meal.spice_level,
            "dietary_tags": candidate.meal.dietary_tags, "allergens": candidate.meal.allergens,
            "location": candidate.meal.location,
            "latitude": candidate.latitude, "longitude": candidate.longitude,
            "image_url": candidate.image_url, "distance_km": round(candidate.distance_km, 1),
            "compatibility_score": compatibility.score, "explanation": compatibility.explanation,
        }
