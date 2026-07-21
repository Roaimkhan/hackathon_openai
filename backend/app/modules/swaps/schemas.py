from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

SwapStatus = Literal["pending", "accepted", "rejected", "completed"]
SwapRole = Literal["all", "sent", "received"]


class CreateSwapRequest(BaseModel):
    meal_id: UUID | None = None
    target_meal_id: UUID | None = None
    requester_meal_id: UUID | None = None
    message: str | None = Field(default=None, max_length=500)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    def validate_meal_ids(cls, values):
        if not isinstance(values, dict):
            return values
        meal_id = values.get("meal_id") or values.get("target_meal_id")
        if meal_id is None:
            raise ValueError("Either meal_id or target_meal_id is required")
        values["meal_id"] = meal_id
        return values


class SwapActionRequest(BaseModel):
    note: str | None = Field(default=None, max_length=500)


class SwapHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    swap_request_id: UUID
    action: str
    actor_id: UUID
    details: dict
    created_at: datetime


class SwapMealResponse(BaseModel):
    id: UUID
    title: str
    image_url: str | None = None


class SwapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    meal_id: UUID
    requester_id: UUID
    recipient_id: UUID
    message: str | None
    status: SwapStatus
    meal: SwapMealResponse
    history: list[SwapHistoryResponse]
    created_at: datetime
    updated_at: datetime
