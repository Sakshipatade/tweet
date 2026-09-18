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

          
