import json, random, string
from fastapi import FastAPI, status, Request, Body,HTTPException, Depends
from fastapi.responses import JSONResponse

from tweet.data import USERS, POSTS, TOKENS
from tweet.routers import users,posts,comments
from tweet.routers.auth import getCurrentUser

from sqlalchemy.orm import Session
from sqlalchemy import text, select
from tweet.models import User
from tweet.database import get_db
from typing import Annotated



app = FastAPI()

dbSession = Annotated[Session, Depends(get_db)]

app.include_router(users.router, tags=["Users"], prefix= "/users")
app.include_router(posts.router, tags=["Posts"])
app.include_router(comments.router, tags=["Comments"])


# login
@app.post("/login")
def loginUser(db:dbSession,username:str=Body(...), password:str = Body(...)):
    user = db.scalar(select(User).where(User.username == username))

    if user is None:
        raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

    if user.password != password:
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
       

# getting all posts
@app.get("/posts")
def getAllPosts(request:Request):
    user = getCurrentUser(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    return POSTS


