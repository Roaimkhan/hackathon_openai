import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SwapRequest(Base):
    __tablename__ = "swap_requests"
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'accepted', 'rejected', 'completed')", name="valid_swap_status"),
        Index(
            "uq_pending_swap_requester_meal",
            "requester_id",
            "meal_id",
            unique=True,
            postgresql_where=text("status = 'pending'"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meals.id"), nullable=False, index=True)
    requester_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    recipient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class SwapHistory(Base):
    __tablename__ = "swap_history"

    id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    swap_request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("swap_requests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
