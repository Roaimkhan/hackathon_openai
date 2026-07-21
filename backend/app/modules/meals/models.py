import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False, default="Homemade meal")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="Freshly prepared homemade food.")
    cuisine: Mapped[str] = mapped_column(String(80), nullable=False, default="Homemade")
    spice_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dietary_tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    allergens: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    taste_notes: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    analysis_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class MealImage(Base):
    __tablename__ = "meal_images"

    id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meals.id", ondelete="CASCADE"), index=True, nullable=False)
    public_url: Mapped[str] = mapped_column(Text, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
