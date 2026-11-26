from fastapi import APIRouter,status, HTTPException,Depends
from fastapi.responses import JSONResponse
from tweet.routers.auth import getCurrentUser
from tweet.pydanticschemas.posts import PostCreate, PostResponse, PostUpdate

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from tweet.database import get_db
from tweet.models.user import User
from tweet.models.post import Post
from tweet.models.comment import Comment

from typing import Annotated

router = APIRouter()

dbSession = Annotated[Session, Depends(get_db)]


# create a new post by the user who is loggedIn
@router.post("/posts")
def createPost(post:PostCreate,db:dbSession,current_user:User | None = Depends(getCurrentUser)):
    
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    # data =  await request.body()
    # body = json.loads(data)
    # body = await request.json()

    new_post = Post(
        content=post.content,
        user_id = current_user.user_id
        )
    
    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(detail="Failed to create Post", status_code= status.HTTP_500_INTERNAL_SERVER_ERROR)from exc
    
    return JSONResponse(content="Post created successfully..", status_code=status.HTTP_201_CREATED)

# getting all posts
@router.get("/posts", response_model=list[PostResponse])
def getAllPosts(db:dbSession, current_user:User|None=Depends(getCurrentUser)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    try:
        posts = db.scalars(select(Post)).all()
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Database failed to retrieve posts", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc
    
    return posts


# getting post of loggedIn user or getting my posts 
@router.get("/myposts", response_model=list[PostResponse])
def getMyPosts(db:dbSession, current_user:User|None=Depends(getCurrentUser)): #authorization:str = Header(...) is for swagger UI for giving the token with the request
    
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    try:
        posts = db.scalars(select(Post).where(Post.user_id == current_user.user_id)).all()
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Database failure to retrieve user post", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc
    
    return posts



# getting all posts of specified user
@router.get("/users/{user_id}/posts", response_model=list[PostResponse])
def getUserPosts(user_id:int, db:dbSession, current_user:User|None=Depends(getCurrentUser)):

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        searched_user = db.scalar(select(User).where(User.user_id == user_id))
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Database failed to retrieve the user",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc

    if searched_user is None:
        raise HTTPException(detail="Searched User not found..",status_code=status.HTTP_404_NOT_FOUND)
    
    try:
        posts = db.scalars(select(Post).where(Post.user_id==user_id)).all()
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Database failed to retrieve the Post",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc


    if not posts:
        raise HTTPException(detail="This user has not posted yet.", status_code=status.HTTP_404_NOT_FOUND)
    
    return posts



# get all posts on which i have commented or loggedIn user commented
@router.get("/me/commented_posts", response_model=list[PostResponse])
def getPostsOnUserCommented(db:dbSession,current_user:User|None=Depends(getCurrentUser)):


    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        posts = db.scalars(
            select(Post)
            .join(Comment, Post.post_id == Comment.post_id)
            .where(Comment.user_id==current_user.user_id)
            .distinct()
            ).all()
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrieve commented posts",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc


    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="You have not commented on any posts yet")

    return posts

# get specific post which i have commmented
@router.get("/me/commented_posts/{post_id}", response_model=PostResponse)
def getPostOnICommented(post_id:int,db:dbSession, current_user:User|None=Depends(getCurrentUser)):

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        post = db.scalar(
            select(Post)
            .join(Comment, Post.post_id==Comment.post_id)
            .where(Comment.user_id==current_user.user_id ,Comment.post_id==post_id)
        )
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrive post", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="You have not commented on any posts yet")

    return post


# update the post of the user by himself only after he is loggedIn
@router.put("/posts/{post_id}")
def updatePost(post_id:int, post:PostUpdate, db:dbSession, current_user:User|None=Depends(getCurrentUser)):


    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        existing_post = db.scalar(select(Post).where(Post.post_id==post_id))
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrieve the post", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc

    if existing_post is None:
        raise HTTPException(detail="Post not found", status_code=status.HTTP_404_NOT_FOUND)

    if existing_post.user_id != current_user.user_id:
        raise HTTPException(detail="You are not allowed to update this post", status_code=status.HTTP_403_FORBIDDEN)

    updated_post = post.model_dump()

    for key,value in updated_post.items():
        setattr(existing_post,key,value)
    try:
        db.commit()
        db.refresh(existing_post)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(detail="failed to update the post", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc


    return JSONResponse(content="Post updated Successfully", status_code=status.HTTP_200_OK)
   

# deleting post of the user who is loggedIn
@router.delete("/posts/{id}")
def deletePost(id:int, db:dbSession, current_user:User|None=Depends(getCurrentUser)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        post = db.scalar(select(Post).where(Post.post_id==id))
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrieve post", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc

    if post is None:
        raise HTTPException(detail="Post not found", status_code=status.HTTP_404_NOT_FOUND)
    
    if post.user_id != current_user.user_id:
        raise HTTPException(detail="You are not allowed to delete this post", status_code=status.HTTP_403_FORBIDDEN)

    try:
        db.delete(post)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(detail="Database failed to delete the post",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc

    return JSONResponse(content="Post deleted successfully", status_code=status.HTTP_200_OK)