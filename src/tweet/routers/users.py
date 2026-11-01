from fastapi import APIRouter, Request, status, HTTPException
from tweet.data import USERS,POSTS, COMMENTS

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