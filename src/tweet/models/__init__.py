from tweet.models.user import User
from tweet.models.post import Post
from tweet.models.comment import Comment
from tweet.models.base import Base
from tweet.models.session import UserSession

#Importing them ensures SQLAlchemy registers all their table definitions in Base.metadata.