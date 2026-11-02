from fastapi import FastAPI, status, Request, Body, Query, Header, HTTPException
from fastapi.responses import JSONResponse
from tweet.data import USERS, COMMENTS, POSTS, TOKENS
from pydantic import BaseModel, Field
import json, random, string
from tweet.routers import users,posts,comments


app = FastAPI()


app.include_router(users.router, tags=["Users"], prefix= "/users")
app.include_router(posts.router, tags=["Posts"])
app.include_router(comments.router, tags=["Comments"])


# Authentication logic
def getCurrentUser(request:Request):
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

            #getting the user associated with that token
            for user in USERS:
                if user.get("user_id") == tk.get("user_id"):
                    return user 
    return None
# this method tells -> This request is coming from user x and the request is authenticated


# login
@app.post("/login")
def loginUser(username:str=Body(...), password:str = Body(...)):
    for user in USERS:
        if user.get('username') == username:
            if user.get('password') == password:

                token = ''.join(random.choices(string.ascii_letters + string.digits, k=6)) #generating random token

                # checking if there is any previous token assigned to that user, if yes removing that token
                # for tk in TOKENS:
                #     if tk.get("user_id") == user.get("user_id"):
                #         TOKENS.remove(tk)

                # Another way: Create a list containing everything except this that user's tokens, then put those contents back into the existing TOKENS list.
                TOKENS[:] = [tk for tk in TOKENS if tk.get("user_id") != user.get("user_id")]

                # appending new token
                TOKENS.append({"token":token, "user_id":user.get("user_id")})

                return JSONResponse(content={"msg":"login successful", "token": f'Token-{token}'}, status_code=status.HTTP_200_OK)
            else:
                return JSONResponse(content="Invalid Password", status_code=400)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")


# getting all posts
@app.get("/posts")
def getAllPosts(request:Request):
    user = getCurrentUser(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    return POSTS



"""  TODO:
1. Priority : use pydantic models for data validation

2. use postgresql 

3. Fix your token format
    Currently you return:

    Token-ahsyw6

    but you're splitting with:

    token_type, token_value = token.split("-")

    That's okay for your learning project, but eventually use the normal HTTP convention:

    Authorization: Bearer ahsyw6

    Then you'll learn why Bearer exists and how real APIs handle authentication.
    

4. Make a proper home-feed endpoint
    You previously wanted the logged-in user to see their posts + other users' posts.

    So add:

    GET /posts

    It should require login and return all posts.

    Later you can make the response richer:

    [
        {
            "post_id": 1,
            "username": "sakshi",
            "content": "FastAPI is a framework of python",
            "comments": [...]
        }
    ]

    That will teach you how backend APIs combine related data.

"""
