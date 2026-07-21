from pydantic import BaseModel, Field


class MealAnalysis(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=10, max_length=500)
    cuisine: str = Field(min_length=2, max_length=80)
    spice_level: int = Field(ge=0, le=5)
    dietary_tags: list[str] = Field(max_length=8)
    allergens: list[str] = Field(max_length=12)
    taste_notes: list[str] = Field(min_length=1, max_length=6)


class CompatibilityResult(BaseModel):
    score: int = Field(ge=0, le=100)
    explanation: str = Field(min_length=8, max_length=180)


class SearchIntentResult(BaseModel):
    cuisine: str | None = Field(default=None, max_length=80)
    max_spice_level: int | None = Field(default=None, ge=0, le=5)
    tags: list[str] = Field(default_factory=list, max_length=8)
    radius_km: float | None = Field(default=None, gt=0, le=100)
