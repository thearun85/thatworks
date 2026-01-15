from sqlalchemy import String, Float, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from .base import Base

class HealthCheck(Base):

    __tablename__ = "health_checks"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String, nullable=False, index=True)
    timeout_s: Mapped[int] = mapped_column(Integer, nullable=False)
    status_code: Mapped[int|None] = mapped_column(Integer, nullable=True)
    is_healthy: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    response_time_ms: Mapped[float|None] = mapped_column(Float, nullable=True)
    error: Mapped[str|None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "timeout_s": self.timeout_s,
            "status_code": self.status_code,
            "is_healthy": self.is_healthy,
            "response_time_ms": self.response_time_ms,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
        }

