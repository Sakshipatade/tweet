from fastapi import FastAPI, status, Request, Body, Query, Header, HTTPException
from fastapi.responses import JSONResponse
from tweet.data import USERS, COMMENTS, POSTS, TOKENS
from pydantic import BaseModel, Field
import json, random, string


app = FastAPI()

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












# get a single comment 
@app.get("/comments/{id}")
def getSpecificComment(request:Request, id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    for comment in COMMENTS:
        if comment.get("comment_id") == id:
            return comment
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found..")
    



# get comments written by a specific user
@app.get("/users/{user_id}/comments")
def getCommentsByUser(request:Request, user_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    requested_user = None

    for user in USERS:
        if user.get("user_id") == user_id:
            requested_user = user
            break

    if requested_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found..")

    
    user_comments = []
    for comment in COMMENTS:
        if comment.get("user_id") == user_id:
            user_comments.append(comment)
    return user_comments




# get a specific comment written by that user
@app.get("/users/{user_id}/comments/{comment_id}")
def getSpecificCommentOfUser(request:Request, user_id:int, comment_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    requested_user = None

    for user in USERS:
        if user.get("user_id") == user_id:
            requested_user = user
            break

    if requested_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found..")

    for comment in COMMENTS:
        if comment.get("user_id") == user_id and comment.get("comment_id") == comment_id:
            return comment
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found..")



# get all comments on any specific posts 
@app.get("/posts/{post_id}/comments")
def getAllCommentsOnAnyPost(request:Request, post_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    
    for post in POSTS:
        if post.get("post_id") == post_id:
            all_comments = []
            for comment in COMMENTS:
                if comment.get("post_id") == post_id:
                    all_comments.append(comment)
            return all_comments
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found..")



# get specific comment on a specific post
@app.get("/posts/{post_id}/comments/{comment_id}")
def getSpecificCommentOfSpecificPost(request:Request, post_id:int, comment_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    post_exists = False

    for post in POSTS:
        if post.get("post_id") == post_id:
            post_exists = True
            break

    if not post_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found..")

    for comment in COMMENTS:
        if comment.get("comment_id") == comment_id and comment.get("post_id") == post_id:
            return comment
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found..")


# TODO: add security
# create a new post 
@app.post("/comments")
async def createComment(request:Request):
    user = getCurrentUser(request)

    if user is None:
        # return JSONResponse(content="You are unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    body = await request.json()

    post_id = body.get("post_id")
    if post_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post Id is Required")

    # check whether the post exists
    # post_exits = False
    # for post in POSTS:
    #     if post.get("post_id") == post_id:
    #         post_exits = True
    #         break
    # OR
    post_exists = any(post.get("post_id") == post_id for post in POSTS)

    if not post_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found..")

    # generate new comment id
    new_comment_id = max(comment.get("comment_id") for comment in COMMENTS)+1

    # set the author and the comment id on the server
    body["user_id"] = user.get("user_id")
    body["comment_id"] = new_comment_id

    COMMENTS.append(body)

    return JSONResponse(content="comment added successfully", status_code=status.HTTP_201_CREATED)


# update existing comment only by the author of that comment
@app.put("/comments/{comment_id}")
async def updateComment(request:Request, comment_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    for comment in COMMENTS:

        if comment.get("comment_id") == comment_id:
            if user.get("user_id") != comment.get("user_id"):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You does not have the permission to modify this post")

            body = await request.json()

            # We write these lines to prevent the user from changing the Comment Id or the owner of the post through the request body.
            body.pop("comment_id", None)
            body.pop("user_id", None)
            body.pop("post_id",None)

            comment.update(body)

            return JSONResponse(content="Comment updated successfully", status_code=status.HTTP_200_OK)
    return JSONResponse(content="Comment not exists", status_code=status.HTTP_404_NOT_FOUND)



# delete a comment 
@app.delete("/comments/{comment_id}")
def deleteComment(request:Request, comment_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    for comment in COMMENTS:
        if comment.get("comment_id") == comment_id:
            if comment.get("user_id") == user.get("user_id"):
                COMMENTS.remove(comment)
                return JSONResponse(content="Comment Deleted..", status_code=status.HTTP_200_OK)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You does not have the permission to delete this post")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")



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
