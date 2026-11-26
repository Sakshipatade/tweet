import random, string
from fastapi import Request, Depends,Body, status,APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Annotated

from tweet.database import get_db
from tweet.data import TOKENS
from tweet.models.user import User
from tweet.security import verifyPassword

router = APIRouter()

dbSession = Annotated[Session, Depends(get_db)]

# Authentication logic
def getCurrentUser(request:Request, db:dbSession):

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
            try:
                user = db.scalar(select(User).where(User.user_id == tk.get("user_id")))
            except SQLAlchemyError as exc:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to retrieve authenticated user") from exc
            return user
    return None
# this method tells -> This request is coming from user x and the request is authenticated

# login
@router.post("/login")
def loginUser(db:dbSession,username:str=Body(...), password:str = Body(...)):
    try:
        user = db.scalar(select(User).where(User.username == username))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database failed to retrieve user") from exc
    
    if user is None:
        raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

    if not verifyPassword(user.password, password):
        raise HTTPException(detail="Invalid Password", status_code=status.HTTP_400_BAD_REQUEST)

    token = ''.join(random.choices(string.ascii_letters + string.digits, k=6)) #generating random token

                # checking if there is any previous token assigned to that user, if yes removing that token
                # for tk in TOKENS:
                #     if tk.get("user_id") == user.get("user_id"):
                #         TOKENS.remove(tk)

    # Another way: Create a list containing everything except this that user's tokens, then put those contents back into the existing TOKENS list.
    TOKENS[:] = [tk for tk in TOKENS if tk.get("user_id") != user.user_id]

    # appending new token
    TOKENS.append({"token":token, "user_id":user.user_id})
    return JSONResponse(content={"msg":"login successful", "token": f'Token-{token}'}, status_code=status.HTTP_200_OK)
       


