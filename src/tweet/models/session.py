from datetime import datetime

from sqlalchemy import (DateTime, Identity, ForeignKey, Boolean,String, func, false)
from sqlalchemy.orm import Mapped, mapped_column

from tweet.models.base import Base


class UserSession(Base):
    __tablename__= "user_sessions"

    session_id:Mapped[int]= mapped_column(Identity(always=True), primary_key=True)
    user_id:Mapped[int]= mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    tokenHash:Mapped[str] = mapped_column(String(64), unique=True)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at:Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_revoked:Mapped[bool] = mapped_column(Boolean, server_default=false())