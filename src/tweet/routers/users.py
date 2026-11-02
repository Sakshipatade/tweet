from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from tweet.data import USERS,TOKENS
from tweet.routers.auth import getCurrentUser
from tweet.schemas.users import UserCreate, UserUpdate, UserResponse

router = APIRouter()


# create a new user
@router.post("")
async def createUser(user:UserCreate):
    new_user_id = len(USERS) + 1

    new_user = user.model_dump()
    new_user["user_id"] = new_user_id
    USERS.append(new_user)
    return JSONResponse(content="User created successfully", status_code=status.HTTP_200_OK)


# get all other users only after you loggedIn
@router.get("", response_model = list[UserResponse])
def getUsers(request:Request):
    user = getCurrentUser(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    return USERS


# getting profile of himself of the user who is logged In
@router.get("/profile", response_model=UserResponse)
async def getProfile(request:Request):
    user = getCurrentUser(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    return user


# Get/Search user by his id only after u are loggedIN 
@router.get('/{id}', response_model=UserResponse)
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
@router.delete('/{id}')
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
@router.put("/{id}")
async def updateUser(request:Request, id:int, user:UserUpdate):
    current_user = getCurrentUser(request)
  
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    if current_user.get("user_id") != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You does not have the permission to modify the user information.")

    # data = await request.body()
    # body = json.loads(data)
    # OR
    # body = await request.json()
    # await request.json() reads the request body and converts the JSON data into a Python object, usually a dictionary. and No need for json.loads()
    # data = await request.body()       Returns raw body as bytes and You need json.loads(data) afterward


    updated_user = user.model_dump()
    if (updated_user.get("username") == current_user.get("username") and updated_user.get("password") == current_user.get("password")):
        return JSONResponse(content="Records are same as previous one...want to edit your info?")

    current_user.update(updated_user)

    return JSONResponse(content="User record updated successfully.", status_code= status.HTTP_200_OK)

