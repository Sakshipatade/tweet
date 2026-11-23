from datetime import datetime

from sqlalchemy import func, Text, DateTime, Identity, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from tweet.models.base import Base

class Post(Base):
    __tablename__ = "posts"

    post_id:Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    content:Mapped[str] = mapped_column(Text)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    created_at:Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

