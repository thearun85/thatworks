from __future__ import annotations
from sqlalchemy import String, Integer, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models import Base
from datetime import datetime
from typing import Optional

class MonitoredUrl(Base):

    __tablename__ = "monitored_urls"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    name: Mapped[str|None] = mapped_column(String, nullable=True)
    check_interval_s: Mapped[int] = mapped_column(Integer, nullable=False)
    timeout_s: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # scheduling
    next_check_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_checked_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True), nullable=True)
    consecutive_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    scheduler_lock: Mapped[Optional[SchedulerLock]] = relationship("SchedulerLock", back_populates="monitored_url", cascade="all, delete-orphan", uselist=False)

    __table_args__ = (
        Index("idx_active_next_check", "is_active", "next_check_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "name": self.name,
            "check_interval_s": self.check_interval_s,
            "timeout_s": self.timeout_s,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
