from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from tweet.data import TOKENS
from tweet.routers.auth import getCurrentUser
from tweet.pydanticschemas.users import UserCreate, UserUpdate, UserResponse, UserPatch, UserPriviledgeResponse

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from tweet.database import get_db
from tweet.models.user import User

from typing import Annotated

router = APIRouter()

dbSession = Annotated[Session, Depends(get_db)]

# create a new user
@router.post("")
def createUser(user:UserCreate, db:dbSession):
    try:
        existing_user = db.scalar(select(User).where(User.username==user.username))
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to check username", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc
    
    if existing_user:
        raise HTTPException(detail="User already exists!", status_code=status.HTTP_409_CONFLICT)

    new_user = User(username = user.username, password = user.password)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(detail='failed to create user', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc
    
    return JSONResponse(content="User created successfully", status_code=status.HTTP_201_CREATED)


# get all other users only after you loggedIn
@router.get("", response_model = list[UserResponse])
def getUsers(db:dbSession,current_user:User|None = Depends(getCurrentUser)): 
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        users = db.scalars(select(User)).all()
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrive users", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc
    
    return users


# getting profile of himself of the user who is logged In
@router.get("/profile", response_model=UserPriviledgeResponse)
def getProfile(current_user:User | None = Depends(getCurrentUser)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    return current_user
    # current_user = db.scalar(select(User).where(User.user_id == user.user_id))
    # return current_user
    # i comment this because getCurrentUser dependancy already retrives the logged-in user's User object from the database
    # so do not need to check the condition again


# Get/Search user by his id only after u are loggedIN 
@router.get('/{id}', response_model=UserResponse)
def getUser(id:int ,db:dbSession,current_user:User | None = Depends(getCurrentUser)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        searched_user = db.scalar(select(User).where(User.user_id==id))
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrive users", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc

    if searched_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "User not found..")
    
    return searched_user
    # for user in USERS:
    #     if user.get("user_id") == id:
    #         return user
    



# Delete user only if he is authenticated Or delete user by himself only
@router.delete('/{id}')
def deleteUser(id:int,db:dbSession, current_user:User |None = Depends(getCurrentUser)):

    if current_user is None: #None means getCurrentUser failed to return a valid user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    if current_user.user_id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You are not allowed to delete the user...")

    user_id = current_user.user_id #saving the user_id before deletion,this avoids accesing SQLAchemy objects after deletion
    try:
        db.delete(current_user)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(detail="Database error occurred while deleting user", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc
    
    # delete that user's token too
    TOKENS[:] = [tk for tk in TOKENS if tk.get("user_id") != user_id]

    return JSONResponse(content="User deleted successfully", status_code=status.HTTP_200_OK)


# update user by him only, only after he is loggedIn
@router.put("/{id}")
def updateUser(id:int, user:UserUpdate, db:dbSession, current_user:User | None = Depends(getCurrentUser)):
    
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    if current_user.user_id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You does not have the permission to modify the user information.")

    # data = await request.body()
    # body = json.loads(data)
    # OR
    # body = await request.json()
    # await request.json() reads the request body and converts the JSON data into a Python object, usually a dictionary. and No need for json.loads()
    # data = await request.body()       Returns raw body as bytes and You need json.loads(data) afterward


    updated_user = user.model_dump()

    if "username" in updated_user:
        try:
            existing_user = db.scalar(select(User).where(User.username == updated_user.get("username"), User.user_id != current_user.user_id))
        except SQLAlchemyError as exc:
            raise HTTPException(detail="Failed to check username", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc

        if existing_user:
            raise HTTPException(detail="Username already exists", status_code=status.HTTP_409_CONFLICT)


    if (updated_user.get("username") == current_user.username and updated_user.get("password") == current_user.password):
        return JSONResponse(content="Records are same as previous one...want to edit your info?")

    # current_user.update(updated_user) this was used when the current_user was dictionary
    for key,value in updated_user.items():
        setattr(current_user,key,value)
    try:
        db.commit()
        db.refresh(current_user)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(detail="failed to update the user", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc
    
    return JSONResponse(content="User record updated successfully.", status_code= status.HTTP_200_OK)

# update only inputed field
@router.patch("/{id}")
def updateSpecificField(id:int, user:UserPatch, db:dbSession,current_user:User | None = Depends(getCurrentUser)):
    
    if current_user is None:
        raise HTTPException(detail = "User is not authorized", status_code=status.HTTP_401_UNAUTHORIZED)


    if current_user.user_id != id:
        raise HTTPException(detail="You are not allowed to update this.", status_code=status.HTTP_403_FORBIDDEN)
    
    updated_user = user.model_dump(exclude_unset=True)
    if not updated_user:
        raise HTTPException(detail="No fields provided to update", status_code=status.HTTP_400_BAD_REQUEST)


    if "username" in updated_user:
        try:
            existing_user = db.scalar(select(User).where(User.username == updated_user.get("username"), User.user_id != current_user.user_id))
        except SQLAlchemyError as exc:
            raise HTTPException(detail="Failed to check username", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc

        if existing_user:
            raise HTTPException(detail="Username already exists", status_code=status.HTTP_409_CONFLICT)


    for field,value in updated_user.items():
        # if value == " " or value is None: used below bcz it also check multiple spaces,empty strings and all
        if value is None or (isinstance(value, str) and not value.strip()):
            raise HTTPException(detail=f'{field} cannot be empty', status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
        else:
            setattr(current_user,field,value)

    # current_user.update(changes)
    try:
        db.commit()
        db.refresh(current_user)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(detail="failed to update the user", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc
    
    return JSONResponse(content="User updated successfully..", status_code=status.HTTP_200_OK)

    