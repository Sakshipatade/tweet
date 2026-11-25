from fastapi import Request, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Annotated

from tweet.database import get_db
from tweet.data import TOKENS
from tweet.models.user import User



dbSession = Annotated[Session, Depends(get_db)]

# Authentication logic
def getCurrentUser(request:Request, db:dbSession):
    # if AuthHeader is not None:
    #     token = AuthHeader
    # else:
    token = request.headers.get("Authorization")

    # checking if the header is missing 
    if not token:
        return None

    # checking if the format is correct
    parts = token.split("-")

    if len(parts) != 2:
        return None

    token_type, token_id = parts

    if token_type != "Token" or not token_id:
        return None

    # finding the token
    for tk in TOKENS:
        if tk.get("token") == token_id:
            user = db.scalar(select(User).where(User.user_id == tk.get("user_id")))
            return user
    return None
# this method tells -> This request is coming from user x and the request is authenticated