from datetime import datetime

from sqlalchemy import Text, ForeignKey, Identity, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from tweet.models.base import Base

class Comment(Base):
    __tablename__ = "comments"

    comment_id:Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    comment_content:Mapped[str] = mapped_column(Text)
    post_id:Mapped[int] = mapped_column(ForeignKey("posts.post_id", ondelete="CASCADE"))
    user_id:Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"))
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    