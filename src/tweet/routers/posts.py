from fastapi import APIRouter, Request, status, HTTPException,Depends
from fastapi.responses import JSONResponse
from tweet.data import POSTS, COMMENTS
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
        raise HTTPException("Failed to create Post", status_code= status.HTTP_500_INTERNAL_SERVER_ERROR)from exc
    
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

    # user_posts = []
    # for post in POSTS:
    #     if post.get("user_id") == user.get("user_id"):
    #         user_posts.append(post)
    # return user_posts


# getting all posts of specified user
@router.get("/users/{user_id}/posts", response_model=list[PostResponse])
def getUserPosts(user_id:int, db:dbSession, current_user:User|None=Depends(getCurrentUser)):

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        posts = db.scalars(select(Post).where(Post.user_id==user_id)).all()
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Database failed to retrieve the user",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc


    if not posts:
        raise HTTPException(detail="This user has not posted yet.", status_code=status.HTTP_404_NOT_FOUND)
    
    return posts
    # user_posts = []
    # for post in POSTS:
    #     if post.get("user_id") == user_id:
    #         user_posts.append(post)
    # return user_posts


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

    # all_posts = []
    # for comment in COMMENTS:
    #     if comment.get("user_id") == user.get("user_id"):
    #         for post in POSTS:
    #             if post.get("post_id") == comment.get("post_id"):
    #                 if post not in all_posts:
    #                     all_posts.append(post)

    # return all_posts



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
    # for comment in COMMENTS:
    #     if comment.get("user_id") == user.get("user_id") and comment.get("post_id") == post_id:
    #         for post in POSTS:
    #             if post_id == post.get("post_id"):
    #                 return post
    # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found or You are not commented on the post")

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

    # for post in POSTS:
    #     if post.get("post_id") == id:
    #         if post.get("user_id") == user.get("user_id"):
    #             POSTS.remove(post)
    #             return JSONResponse(content="Post deleted successfully.", status_code=status.HTTP_200_OK)
    #         else:
    #             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You does have the permission to delete this post..")
    # raise HTTPException(detail="Post not found", status_code=status.HTTP_404_NOT_FOUND)


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
        raise HTTPException(detail="You are not allowed to update this post", status_code=status.HTTP_409_CONFLICT)

    updated_post = post.model_dump()

    for key,value in updated_post.items():
        setattr(existing_post,key,value)
    try:
        db.commit()
        db.refresh(existing_post)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(detail="failed to update the user", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc


    return JSONResponse(content="Post updated Successfully", status_code=status.HTTP_200_OK)
    # for existing_post in POSTS:
    #     if existing_post.get("post_id") == post_id:

    #         if existing_post.get("user_id") != user.get("user_id"):
    #             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You does not have the permission to modify this post")


    #         # body = await request.json()
    #         # # We write these two lines to prevent the user from changing the post ID or the owner of the post through the request body.
    #         # body.pop("post_id", None)
    #         # body.pop("user_id", None)

    #         updated_post = post.model_dump()
    #         existing_post.update(updated_post)
    #         return JSONResponse(content="Post updated sucessfully..", status_code=status.HTTP_200_OK)
        
    # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found..")

