import asyncio
import logging
import re

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.modules.ai.schemas import CompatibilityResult, MealAnalysis, SearchIntentResult

logger = logging.getLogger(__name__)


class AIService:
    """The sole boundary where TableSwap communicates with OpenAI."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def analyze_meal(
        self, *, image_url: str, title_hint: str | None = None, description_hint: str | None = None
    ) -> MealAnalysis | None:
        if not self.settings.openai_api_key:
            logger.warning("Meal analysis skipped: OPENAI_API_KEY is not configured")
            return None
        prompt = (
            "Analyze this single homemade meal image. Identify only what is reasonably visible. "
            "Return concise customer-facing metadata. Allergens must be conservative and only named when plausible. "
            f"User title hint: {title_hint or 'none'}. User description hint: {description_hint or 'none'}."
        )
        try:
            client = AsyncOpenAI(
                api_key=self.settings.openai_api_key.get_secret_value(),
                timeout=self.settings.openai_timeout_seconds,
            )
            response = await asyncio.wait_for(
                client.responses.create(
                    model=self.settings.openai_model,
                    instructions="You are TableSwap's meal analysis engine. Return exactly the requested JSON schema.",
                    input=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": prompt},
                                {"type": "input_image", "image_url": image_url},
                            ],
                        }
                    ],
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": "meal_analysis",
                            "strict": True,
                            "schema": MealAnalysis.model_json_schema(),
                        }
                    },
                ),
                timeout=self.settings.openai_timeout_seconds + 2,
            )
            return MealAnalysis.model_validate_json(response.output_text)
        except Exception as exc:
            # Analysis is deliberately non-blocking for the meal upload journey.
            logger.warning("Meal analysis unavailable: %s", exc)
            return None

    async def calculate_compatibility(
        self, *, taste_profile: dict, meal: dict, distance_km: float
    ) -> CompatibilityResult | None:
        """Return a GPT decision; callers own deterministic fallbacks and time budgets."""
        if not self.settings.openai_api_key:
            return None
        try:
            client = AsyncOpenAI(
                api_key=self.settings.openai_api_key.get_secret_value(),
                timeout=2.0,
            )
            response = await client.responses.create(
                model=self.settings.openai_model,
                instructions=(
                    "You are TableSwap's compatibility engine. Score how well a meal fits a diner. "
                    "Prioritize dietary requirements, then stated preferences, then distance. "
                    "Return only the requested JSON schema."
                ),
                input=(
                    "Diner taste profile: " + str(taste_profile) + "\n"
                    "Meal: " + str(meal) + "\n"
                    f"Distance: {distance_km:.1f} km"
                ),
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "compatibility_result",
                        "strict": True,
                        "schema": CompatibilityResult.model_json_schema(),
                    }
                },
            )
            return CompatibilityResult.model_validate_json(response.output_text)
        except Exception as exc:
            logger.info("Compatibility scoring unavailable: %s", exc)
            return None

    async def parse_search_intent(self, query: str) -> SearchIntentResult:
        """Interpret a natural-language query without making search availability depend on GPT."""
        if not self.settings.openai_api_key:
            return self._fallback_search_intent(query)
        try:
            client = AsyncOpenAI(
                api_key=self.settings.openai_api_key.get_secret_value(),
                timeout=self.settings.openai_timeout_seconds,
            )
            response = await asyncio.wait_for(
                client.responses.create(
                    model=self.settings.openai_model,
                    instructions=(
                        "Extract meal-search filters from the user's request. "
                        "Use null for unknown cuisine, maximum spice, and radius. "
                        "Tags must contain only dietary requirements or preferences explicitly requested."
                    ),
                    input=query,
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": "search_intent",
                            "strict": True,
                            "schema": SearchIntentResult.model_json_schema(),
                        }
                    },
                ),
                timeout=self.settings.openai_timeout_seconds,
            )
            return SearchIntentResult.model_validate_json(response.output_text)
        except Exception as exc:
            logger.info("Search intent parsing unavailable: %s", exc)
            return self._fallback_search_intent(query)

    @staticmethod
    def _fallback_search_intent(query: str) -> SearchIntentResult:
        """Extract common search filters when the AI service is unavailable."""
        normalized = query.lower()
        cuisines = (
            "pakistani", "indian", "italian", "chinese", "thai", "mexican",
            "japanese", "korean", "mediterranean", "american", "homemade",
        )
        cuisine = next((value for value in cuisines if re.search(rf"\b{value}\b", normalized)), None)

        tag_patterns = {
            "vegan": "vegan",
            "vegetarian": "vegetarian",
            "halal": "halal",
            "keto": "keto",
            "gluten[- ]?free": "gluten-free",
            "dairy[- ]?free": "dairy-free",
            "high[- ]?protein": "high-protein",
        }
        tags = [tag for pattern, tag in tag_patterns.items() if re.search(rf"\b{pattern}\b", normalized)]

        max_spice_level = None
        if re.search(r"\b(no|not|non)[ -]?spicy\b|\bmild\b", normalized):
            max_spice_level = 1
        elif re.search(r"\bmedium\b", normalized):
            max_spice_level = 3
        elif re.search(r"\bspicy\b|\bhot\b", normalized):
            max_spice_level = 5

        radius_match = re.search(r"\b(?:within|under|less than)\s+(\d+(?:\.\d+)?)\s*(?:km|kilometers?)\b", normalized)
        return SearchIntentResult(
            cuisine=cuisine,
            max_spice_level=max_spice_level,
            tags=tags,
            radius_km=float(radius_match.group(1)) if radius_match else None,
        )
