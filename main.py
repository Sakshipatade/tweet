from fastapi import FastAPI, status, Request, Body
from fastapi.responses import JSONResponse
from tweet.data import USERS, COMMENTS, POSTS
import json


app = FastAPI()


# create a new user
@app.post("/users")
async def createUser(request:Request):
    data = await request.body()
    body = json.loads(data)
    if type(body.get("username")) is str:
        USERS.append(body)
    return JSONResponse(content={"msg" : "user created"}, status_code=status.HTTP_201_CREATED)


# get all users
@app.get("/users")
def getUsers():
    return USERS

# login
@app.post("/login")
def loginUser(username:str=Body(...), password:str = Body(...)):
    for user in USERS:
        if user.get('username') == username:
            if user.get('password') == password:
                return JSONResponse(content={"msg":"login successful", "token":f"T-{user.get("user_id")}"}, status_code=status.HTTP_200_OK)
            else:
                return JSONResponse(content="Invalid Password", status_code=400)
    return JSONResponse(content="Username not found", status_code=404)





# profile 
@app.get("/profile")
async def getProfile(request:Request):
    # headers = request.headers
    token = request.headers.get('Authorization')
    token_type, token_id = token.split('-')
    token_id=int(token_id)
    for user in USERS:
        # print(user, token_id)
        # print(token_id == user.get("user_id"))
        if token_id == user.get("user_id"):
            return user
    return JSONResponse(content="Invalid token", status_code=status.HTTP_401_UNAUTHORIZED)

# Get user by his id
@app.get('/users/{id}')
def getUser(id:int):
    for user in USERS:
        if user.get("user_id") == id:
            return user

    return JSONResponse(content = "user not found", status_code = 404)


