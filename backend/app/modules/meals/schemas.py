from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MealDraftCreate(BaseModel):
    title: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    location: str | None = Field(default=None, max_length=255)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class MealCreate(MealDraftCreate):
    """Alias kept for the public create-meal contract."""


class MealImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    public_url: str
    position: int


class MealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    owner_id: UUID
    title: str
    description: str
    cuisine: str
    spice_level: int
    dietary_tags: list[str]
    allergens: list[str]
    taste_notes: list[str]
    analysis_status: str
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    images: list[MealImageResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
