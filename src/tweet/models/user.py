from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, true, func, Identity
from sqlalchemy.orm import Mapped, mapped_column

from tweet.models.base import Base

class User(Base):
    __tablename__ = "users"

    user_id:Mapped[int] = mapped_column(Identity(always=True),primary_key=True)
    username:Mapped[str] = mapped_column(String(50), unique=True)
    password:Mapped[str] = mapped_column(String(250))
    created_at:Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active:Mapped[bool] = mapped_column(Boolean, server_default=true())

