from fastapi import FastAPI, status, Request, Body, Query, Header
from fastapi.responses import JSONResponse
from tweet.data import USERS, COMMENTS, POSTS, TOKENS
import json, random, string

app = FastAPI()

# Authentication logic
def getCurrentUser(request:Request):
    token = request.headers.get("Authorization")
    token_type, token_id = token.split("-")

    if token_type == "Token":
        for tk in TOKENS:
            if tk.get("token") == token_id:
                for user in USERS:
                    if user.get("user_id") == tk.get("user_id"):
                        return user #getting the user associated with that token
        return None
# this method tells -> This request is coming from user x and the request is authenticated


# create a new user
@app.post("/users")
async def createUser(request:Request):
    # data = await request.body()
    # # print(data)
    # body = json.loads(data)

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
    return JSONResponse(content="User not found", status_code=404)



# get all other users only after you loggedIn
@app.get("/users")
def getUsers(request:Request):
    user = getCurrentUser(request)
    if user is None:
        return JSONResponse(content="Unauthorized", status_code = status.HTTP_401_UNAUTHORIZED)
    return USERS



# getting profile of himself of the user who is logged In
@app.get("/profile")
async def getProfile(request:Request):
    user = getCurrentUser(request)
    if user is None:
        return JSONResponse(content="Unauthorized", status_code = status.HTTP_401_UNAUTHORIZED)
    return user




# getting post of loggedIn user
@app.get("/users/posts")
def getMyPosts(request:Request): #authorization:str = Header(...) is for swagger UI for giving the token with the request
    user = getCurrentUser(request)

    if user is None:
        return JSONResponse(content="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

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
        return JSONResponse(content="Unauthorized", status_code = status.HTTP_401_UNAUTHORIZED)

    for u in USERS:
        if u.get("user_id") == id:
            return u

    return JSONResponse(content = {"error" : "user not found"}, status_code = 404)



# Delete user only if he is authenticated Or delete me by me only
@app.delete('/users/{id}')
def deleteUser(request:Request,id:int):
    user = getCurrentUser(request)

    if user is None: #None means getCurrentUser failed to return a valid user
        return JSONResponse(content="unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

    if user.get("user_id") != id:
        return JSONResponse(content="You are not allowed to delete", status_code=status.HTTP_403_FORBIDDEN)

    USERS.remove(user)

    # delete that user's token too
    TOKENS[:] = [tk for tk in TOKENS if tk.get("user_id") != user.get("user_id")]

    return JSONResponse(content="user deleted successfully", status_code=status.HTTP_200_OK)



# getting all posts
@app.get("/posts")
def getAllPosts(request:Request):
    user = getCurrentUser(request)
    if user is None:
        return JSONResponse(content="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
    return POSTS



# getting all posts of specified user
@app.get("/users/{user_id}/posts")
def getUserPosts(request:Request, user_id:int):
    user = getCurrentUser(request)
    print("Current User: ", user)

    if user is None:
        return JSONResponse(content="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
    
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
        return JSONResponse(content="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

    for post in POSTS:
        if post.get("post_id") == post_id and post.get("user_id") == user_id:
            return post
    return JSONResponse(content="Post not found", status_code=status.HTTP_404_NOT_FOUND)
    


# deleting post of the user who is loggedIn
@app.delete("/posts/{id}")
def deletePost(request:Request, id:int):
    user = getCurrentUser(request)
    if user is None:
        return JSONResponse(content="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

    for post in POSTS:
        if post.get("post_id") == id:
            if post.get("user_id") == user.get("user_id"):
                POSTS.remove(post)
                return JSONResponse(content="Post deleted..", status_code=status.HTTP_200_OK)
            else:
                return JSONResponse(content="You are not allowed to delete this post", status_code=status.HTTP_403_FORBIDDEN)



# create a new post by the user who is loggedIn
@app.post("/posts")
async def createPost(request:Request):
    user = getCurrentUser(request)

    if user is None:
        return JSONResponse(content="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

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
        return JSONResponse(content="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

    if user.get("user_id") != id:
        return JSONResponse(content="You are not allowed to do this", status_code=status.HTTP_403_FORBIDDEN)

    # data = await request.body()
    # body = json.loads(data)

    # OR

    body = await request.json()
    # await request.json() reads the request body and converts the JSON data into a Python object, usually a dictionary. and No need for json.loads()
    # data = await request.body()       Returns raw body as bytes and You need json.loads(data) afterward

    if "username" not in body or "password" not in body:
        return JSONResponse(content="Username and Password are required..", status_code=status.HTTP_400_BAD_REQUEST)


    if (user.get("username") == body.get("username") and user.get("password") == body.get("password")):
        return JSONResponse(content="Records are same as previous one...want to edit your info?")


    user.update({
        "username" : body["username"],
        "password" : body["password"]
    })

    return JSONResponse(content="record updated..", status_code= status.HTTP_200_OK)
    


"""  Things to do:
1. u have to use database now

2. Fix your token format
    Currently you return:

    Token-ahsyw6

    but you're splitting with:

    token_type, token_value = token.split("-")

    That's okay for your learning project, but eventually use the normal HTTP convention:

    Authorization: Bearer ahsyw6

    Then you'll learn why Bearer exists and how real APIs handle authentication.

3. complete the CRUD 
    PUT    /posts/{post_id}
    PUT    /users/{user_id}

    The important authorization rule should be:

    Logged-in user
        ↓
    Can see all posts
        ↓
    Can create a post
        ↓
    Can update ONLY own post
        ↓
    Can delete ONLY own post

    For example, if Sakshi owns:

    {
        "post_id": 1,
        "user_id": 1,
        "content": "FastAPI is a framework of python"
    }

    and Vaishnavi (user_id = 2) sends:

    PUT /posts/1

    your API should reject it because:

    logged_in_user_id = 2
    post_owner_id     = 1

    2 != 1

    This is the authorization part.

    

4. Add comments CRUD
    Your COMMENTS structure is already correct for this.

    Implement:

    POST   /posts/{post_id}/comments
    GET    /posts/{post_id}/comments
    PUT    /comments/{comment_id}
    DELETE /comments/{comment_id}

    For creating a comment:

    logged-in user
        +
    post_id
        ↓
    create comment

    You should not ask the client for user_id.

    For example:

    {
        "post_id": 3,
        "comment_content": "Nice post"
    }

    The server gets the user_id from the token.

    So conceptually:

    Token
    ↓
    user_id = 1

    POST /posts/3/comments
    ↓
    comment = {
        "comment_id": 115,
        "user_id": 1,
        "post_id": 3,
        "comment_content": "Nice post"
    }

    This is an important backend concept.


5. Make a proper home-feed endpoint
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


7. Handle invalid/missing tokens
    Right now this can cause problems:

    token = request.headers.get("Authorization")
    token_type, token_id = token.split("-")

    What if there is no header?

    Authorization header missing

    What if the token is wrong?

    Authorization: Bearer abcxyz


    What if the format is wrong?

    Authorization: hello

    Your API should return:

    401 Unauthorized

    instead of crashing.
"""
