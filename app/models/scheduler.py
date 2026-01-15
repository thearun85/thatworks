from __future__ import annotations
from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.models import Base

class SchedulerLock(Base):

    __tablename__ = "scheduler_locks"
    
    monitored_url_id: Mapped[int] = mapped_column(ForeignKey("monitored_urls.id", ondelete="CASCADE"), primary_key=True)

    locked_by: Mapped[str] = mapped_column(String, nullable=False) # scheduler instance id
    locked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    monitored_url: Mapped[MonitoredUrl] = relationship("MonitoredUrl", back_populates="scheduler_lock")

    __table_args__ = (
        Index("idx_expires_at", "expires_at"),
    )
