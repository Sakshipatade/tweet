from fastapi import FastAPI, status, Request, Body, Query, Header, HTTPException
from fastapi.responses import JSONResponse
from tweet.data import USERS, COMMENTS, POSTS, TOKENS
import json, random, string


app = FastAPI()

# Authentication logic
def getCurrentUser(request:Request):
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



# create a new user
@app.post("/users")
async def createUser(request:Request):
    body = await request.json()
    new_user_id = len(USERS) + 1
    # print(new_user_id)
    body["user_id"] = new_user_id
    USERS.append(body)
    return USERS[-1] #returning the last new record added to list



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



# get all other users only after you loggedIn
@app.get("/users")
def getUsers(request:Request):
    user = getCurrentUser(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    return USERS



# getting profile of himself of the user who is logged In
@app.get("/profile")
async def getProfile(request:Request):
    user = getCurrentUser(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    return user




# getting post of loggedIn user or getting my posts 
@app.get("/users/posts")
def getMyPosts(request:Request): #authorization:str = Header(...) is for swagger UI for giving the token with the request
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    user_posts = []
    for post in POSTS:
        if post.get("user_id") == user.get("user_id"):
            user_posts.append(post)
    return user_posts



# Get/Search user by his id only after u are loggedIN 
@app.get('/users/{id}')
def getUser(request:Request,id:int):
    user = getCurrentUser(request)
    print(user)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    for user in USERS:
        if user.get("user_id") == id:
            return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "User not found..")



# Delete user only if he is authenticated Or delete me by me only
@app.delete('/users/{id}')
def deleteUser(request:Request,id:int):
    user = getCurrentUser(request)

    if user is None: #None means getCurrentUser failed to return a valid user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    if user.get("user_id") != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You are not allowed to delete the user...")

    USERS.remove(user)

    # delete that user's token too
    TOKENS[:] = [tk for tk in TOKENS if tk.get("user_id") != user.get("user_id")]

    return JSONResponse(content="User deleted successfully", status_code=status.HTTP_200_OK)



# getting all posts
@app.get("/posts")
def getAllPosts(request:Request):
    user = getCurrentUser(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    return POSTS



# getting all posts of specified user
@app.get("/users/{user_id}/posts")
def getUserPosts(request:Request, user_id:int):
    user = getCurrentUser(request)
    print("Current User: ", user)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    
    user_posts = []
    for post in POSTS:
        if post.get("user_id") == user_id:
            user_posts.append(post)
    return user_posts



# getting a specified post of a specified user
@app.get("/users/{user_id}/posts/{post_id}")
def getUserPost(request:Request, user_id:int, post_id:int):
    user = getCurrentUser(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    for post in POSTS:
        if post.get("post_id") == post_id and post.get("user_id") == user_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Post not found..")
    


# deleting post of the user who is loggedIn
@app.delete("/posts/{id}")
def deletePost(request:Request, id:int):
    user = getCurrentUser(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    for post in POSTS:
        if post.get("post_id") == id:
            if post.get("user_id") == user.get("user_id"):
                POSTS.remove(post)
                return JSONResponse(content="Post deleted successfully.", status_code=status.HTTP_200_OK)
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You does have the permission to delete this post..")



# create a new post by the user who is loggedIn
@app.post("/posts")
async def createPost(request:Request):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    # data =  await request.body()
    # body = json.loads(data)
    body = await request.json()

    new_post_id = max(post.get("post_id") for post in POSTS) + 1

    body["user_id"] = user.get("user_id")
    body["post_id"] = new_post_id
    POSTS.append(body)
    return JSONResponse(content="Post created successfully..", status_code=status.HTTP_201_CREATED)



# update user by him only, only after he is loggedIn
@app.put("/users/{id}")
async def updateUser(request:Request, id:int):
    user = getCurrentUser(request)
  
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    if user.get("user_id") != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You does not have the permission to modify the user information.")

    # data = await request.body()
    # body = json.loads(data)

    # OR

    body = await request.json()
    # await request.json() reads the request body and converts the JSON data into a Python object, usually a dictionary. and No need for json.loads()
    # data = await request.body()       Returns raw body as bytes and You need json.loads(data) afterward

    if "username" not in body or "password" not in body:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and Password are required.")


    if (user.get("username") == body.get("username") and user.get("password") == body.get("password")):
        return JSONResponse(content="Records are same as previous one...want to edit your info?")


    user.update({
        "username" : body["username"],
        "password" : body["password"]
    })

    return JSONResponse(content="User record updated successfully.", status_code= status.HTTP_200_OK)



    
# update the post of the user by himself only after he is loggedIn
@app.put("/posts/{post_id}")
async def updatePost(request:Request, post_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    for post in POSTS:
        if post.get("post_id") == post_id:

            if post.get("user_id") != user.get("user_id"):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You does not have the permission to modify this post")


            body = await request.json()

            # We write these two lines to prevent the user from changing the post ID or the owner of the post through the request body.
            body.pop("post_id", None)
            body.pop("user_id", None)

            post.update(body)
            return JSONResponse(content="Post updated sucessfully..", status_code=status.HTTP_200_OK)
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found..")




# get all comments only after user is loggedIn
@app.get("/comments")
def getAllComments(request:Request):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    return COMMENTS



# get comments written by me OR current loggedIn user
@app.get("/comments/me")
def getMyComments(request:Request):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    all_comments = []
    for comment in COMMENTS:
        if comment.get("user_id") == user.get("user_id"):
            all_comments.append(comment)
    return all_comments



# get all comments on my all posts
@app.get("/me/comments/received")
def getCommentsOnMyPosts(request:Request):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    all_comments = []

    for post in POSTS:
        if user.get("user_id") == post.get("user_id"):
            for comment in COMMENTS:
                if post.get("post_id") == comment.get("post_id"):
                    all_comments.append(comment)
    return all_comments



# get all posts on which i have commented or loggedIn user commented
@app.get("/me/commented_posts")
def getPostsOnUserCommented(request:Request):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    all_posts = []
    for comment in COMMENTS:
        if comment.get("user_id") == user.get("user_id"):
            for post in POSTS:
                if post.get("post_id") == comment.get("post_id"):
                    if post not in all_posts:
                        all_posts.append(post)

    return all_posts



# get specific post which i have commmented
@app.get("/me/commented_posts/{post_id}")
def getPostOnICommented(request:Request, post_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")


    for comment in COMMENTS:
        if comment.get("user_id") == user.get("user_id") and comment.get("post_id") == post_id:
            for post in POSTS:
                if post_id == post.get("post_id"):
                    return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found or You are not commented on the post")



    
# get all comments on my specific posts
@app.get("/me/posts/{post_id}/comments")
def getAllCommentsOnMyPost(request:Request, post_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    all_comments = []
    for post in POSTS:
        if post.get("user_id") == user.get("user_id") and post.get("post_id") == post_id:
            for comment in COMMENTS:
                if comment.get("post_id") == post_id:
                    all_comments.append(comment)
            return all_comments
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found..")




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

1. use postgresql 

2. use pydantic models for data validation

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
