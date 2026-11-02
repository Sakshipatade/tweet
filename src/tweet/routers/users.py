from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from tweet.data import USERS,POSTS, COMMENTS, TOKENS

router = APIRouter()


# create a new user
@router.post("/users")
async def createUser(request:Request):
    body = await request.json()
    new_user_id = len(USERS) + 1
    # print(new_user_id)
    body["user_id"] = new_user_id
    USERS.append(body)
    return USERS[-1] #returning the last new record added to list


# get all other users only after you loggedIn
@router.get("/users")
def getUsers(request:Request):
    user = getCurrentUser(request:Request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    return USERS


# getting profile of himself of the user who is logged In
@router.get("/profile")
async def getProfile(request:Request):
    user = getCurrentUser(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    return user


# getting post of loggedIn user or getting my posts 
@router.get("/users/posts")
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
@router.get('/users/{id}')
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
@router.delete('/users/{id}')
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


# update user by him only, only after he is loggedIn
@router.put("/users/{id}")
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

