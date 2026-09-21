from fastapi import FastAPI, status, Request, Body, Query
from fastapi.responses import JSONResponse
from tweet.data import USERS, COMMENTS, POSTS, TOKENS
import json, random, string



app = FastAPI()


# create a new user
@app.post("/users")
async def createUser(request:Request):
    data = await request.body()
    # print(data)
    body = json.loads(data)
    new_user_id = len(USERS) + 1
    # print(new_user_id)
    body["user_id"] = new_user_id
    USERS.append(body)
    return USERS

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
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=6)) #generating random token
                TOKENS.append({"token":token, "user_id":user.get("user_id")})
                return JSONResponse(content={"msg":"login successful", "token": f'Token-{token}'}, status_code=status.HTTP_200_OK)
            else:
                return JSONResponse(content="Invalid Password", status_code=400)
    return JSONResponse(content="Username not found", status_code=404)



# profile 
@app.get("/profile")
async def getProfile(request:Request):
    # headers = request.headers
    token = request.headers.get('Authorization')
    token_type, token_id = token.split('-')

    if token_type == "T":
        token_id=int(token_id)
        for user in USERS:
            # print(user, token_id)
            # print(token_id == user.get("user_id"))
            if token_id == user.get("user_id"):
                return user
        return JSONResponse(content="Invalid token", status_code=status.HTTP_401_UNAUTHORIZED)

    if token_type == "Token":
        # print(token_type, "received", token)
        for tk in TOKENS:
            # print(tk.get('token') == token_id)
            # print(token_id)
            # print(tk)
            if tk.get("token") == token_id:
                for user in USERS:
                    if user.get("user_id") == tk.get("user_id"):
                        return user




# Get user by his id
@app.get('/users/{id}')
def getUser(id:int):
    for user in USERS:
        if user.get("user_id") == id:
            return user

    return JSONResponse(content = "user not found", status_code = 404)


# Delete user 
@app.delete('/users')
def deleteUser(request:Request):
    token = request.headers.get('Authorization')
    token_type, token_id = token.split('-')
    token = int(token_id)
    # print(token_type, token_id)
    for user in USERS:
        if user.get("user_id") == token:
            USERS.remove(user)
            return JSONResponse(content="User deleted successfully", status_code=status.HTTP_200_OK)
    return JSONResponse(content='Falied to delete user', status_code=status.HTTP_404_NOT_FOUND)



@app.get("/user/posts")
def getUserPosts(request:Request):
    token = request.headers.get("Authorization")
    token_type, token_value = token.split("-")
    # print(token_type, token_value)

    for tk in TOKENS:
        if tk.get("token") == token_value:
            user_posts = []
            for post in POSTS:
                if post.get("user_id") == tk.get("user_id"):
                    user_posts.append(post)
            return user_posts
                #     print("hiii")
                # return post


@app.delete("/user/posts")
def deletePost(request:Request, post_id:int = Query()):
#    print(post_id, type(post_id))
#    print("hello")
   token = request.headers.get("Authorization")
   token_type, token_value = token.split("-")

   for tk in TOKENS:
       if tk.get("token") == token_value:
           for post in POSTS:
               if post.get("post_id") == post_id:
                   POSTS.remove(post)


"""  Things to do:


1. Fix your authentication logic first in getUser

    Before adding more endpoints, make one reusable function such as:

    def get_current_user(request: Request):
        ...

    Its job should be:

    Authorization header
            ↓
    extract token
            ↓
    find token in TOKENS
            ↓
    get user_id
            ↓
    find user in USERS
            ↓
    return user

    Then instead of repeating this:

    token = request.headers.get("Authorization")
    token_type, token_value = token.split("-")

    for tk in TOKENS:
        ...

    in every endpoint, you can do:

    user = get_current_user(request)

    This is the next concept I would learn, because almost every protected endpoint will need it.


2. Fix your token format
    Currently you return:

    Token-ahsyw6

    but you're splitting with:

    token_type, token_value = token.split("-")

    That's okay for your learning project, but eventually use the normal HTTP convention:

    Authorization: Bearer ahsyw6

    Then you'll learn why Bearer exists and how real APIs handle authentication.


3. complete the CRUD 
    POST   /posts
    GET    /posts   
    GET    /posts/{post_id}
    PUT    /posts/{post_id}
    DELETE /posts/{post_id}
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


6. Add user update

    You currently have this commented:

    # @app.put("/users/{id}")
    # def updateUserInfo(id:int):

    Implement it with authentication.

    The client should not be allowed to say:

    PUT /users/2

    while logged in as user 1 and modify user 2.

    Instead:

    Token → user_id = 1
            ↓
    modify user 1

    This reinforces the same authorization concept.


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

