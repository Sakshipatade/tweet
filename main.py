from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from tweet.data import USERS, COMMENTS, POSTS
import json
# from pydantic import BaseModel, Field


app = FastAPI()


# create a new user
@app.post("/users")
async def createUser(request:Request):
    data = await request.body()
    body = json.loads(data)
    USERS.append(body)
    return JSONResponse(content={"msg" : "user created"}, status_code=status.HTTP_201_CREATED)


# get all users
@app.get("/users")
def getUsers():
    return USERS
