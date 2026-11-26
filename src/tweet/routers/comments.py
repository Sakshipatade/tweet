from fastapi import APIRouter, Request, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from tweet.data import USERS,POSTS, COMMENTS
from tweet.routers.auth import getCurrentUser
from tweet.pydanticschemas.comments import CommentCreate, CommentResponse, CommentUpdate

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from tweet.database import get_db
from tweet.models.user import User
from tweet.models.comment import Comment
from tweet.models.post import Post

from typing import Annotated

router = APIRouter()

dbSession = Annotated[Session, Depends(get_db)]

# create a new comment 
@router.post("/comments")
def createComment(comment:CommentCreate, db:dbSession, current_user:User|None = Depends(getCurrentUser)):

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    new_comment =Comment(
        user_id = current_user.user_id,
        post_id = comment.post_id,
        comment_content = comment.comment_content)

    try:
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(detail="Failed to create Post", status_code= status.HTTP_500_INTERNAL_SERVER_ERROR)from exc
    
    return JSONResponse(content="Comment created successfully..", status_code=status.HTTP_201_CREATED)



# get all comments only after user is loggedIn
@router.get("/comments", response_model=list[CommentResponse])
def getAllComments(db:dbSession, current_user:User|None = Depends(getCurrentUser)):

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        comments = db.scalars(select(Comment)).all()
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrieve comments", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc

    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Comments not found")
    
    return comments


# get comments written by me OR current loggedIn user
@router.get("/comments/me", response_model=list[CommentResponse])
def getMyComments(db:dbSession, current_user:User|None = Depends(getCurrentUser)):

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        comments = db.scalars(select(Comment).where(Comment.user_id==current_user.user_id)).all()
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrieve comments", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc

    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Comments not found")
 
    return comments



# get all comments on my all posts
@router.get("/me/comments/received", response_model=list[CommentResponse])
def getCommentsOnMyPosts(db:dbSession, current_user:User|None = Depends(getCurrentUser)):

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        comments = db.scalars(select
        (Comment)
        .join(Post, Post.post_id==Comment.post_id)
        .where(Post.user_id == current_user.user_id)
        ).all()
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrieve comments", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
    
    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="You have not received any comment yet")
 
    return comments



# get all comments on my specific posts
@router.get("/me/posts/{post_id}/comments", response_model=list[CommentResponse])
def getAllCommentsOnMyPost(post_id:int,db:dbSession, current_user:User|None = Depends(getCurrentUser)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        existing_post = db.scalar(select(Post)
        .where (
            Post.post_id == post_id,
            Post.user_id == current_user.user_id
        ))
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrieve post", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
    
    if existing_post is None:
        raise HTTPException(detail="Post not found", status_code=status.HTTP_404_NOT_FOUND)
    
    try:
        comments = db.scalars(select(Comment).where(Comment.post_id == post_id)).all()
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrieve comments", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
    
    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Comments not found")
 
    return comments



# get a single comment 
@router.get("/comments/{id}", response_model=CommentResponse)
def getSpecificComment(id:int, db:dbSession, current_user:User|None = Depends(getCurrentUser)):

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        comment = db.scalar(select(Comment).where(Comment.comment_id == id))
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrieve comment", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Comments not found")
    return comment
 

# get comments written by a specific user
@router.get("/users/{user_id}/comments", response_model=list[CommentResponse])
def getCommentsByUser(user_id:int,db:dbSession, current_user:User|None = Depends(getCurrentUser)):

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    user = db.scalar(select(User). where(User.user_id == user_id))

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")


    try:
        comments = db.scalars(select(Comment).where(Comment.user_id == user_id)).all()
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrieve comments", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc

    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="This user has not written any comments yet")
    return comments


# get a specific comment written by that user
@router.get("/users/{user_id}/comments/{comment_id}", response_model=CommentResponse)
def getSpecificCommentOfUser(user_id:int, comment_id:int, db:dbSession, current_user:User|None = Depends(getCurrentUser)):

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        searched_user = db.scalar(select(User).where(User.user_id == user_id))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to retrieve user") from exc

    if searched_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")


    try:
        comment = db.scalar(select(Comment).where(Comment.comment_id == comment_id, Comment.user_id == user_id))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to retrieve comment") from exc

    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Comment not found")

    return comment
    


# get all comments on any specific posts 
@router.get("/posts/{post_id}/comments", response_model=list[CommentResponse])
def getAllCommentsOnAnyPost(post_id:int, db:dbSession, current_user:User|None = Depends(getCurrentUser)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    try:
        post = db.scalar(
            select(Post).where(Post.post_id == post_id)
        )
    except SQLAlchemyError as exc:
       raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to retrieve post") from exc 

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found")
    
    try:
        comments = db.scalars(select(Comment).where(
            Comment.post_id == post_id
        )).all()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to retrieve comments") from exc

    return comments


# get specific comment on a specific post
@router.get("/posts/{post_id}/comments/{comment_id}", response_model=CommentResponse)
def getSpecificCommentOfSpecificPost(post_id:int, comment_id:int,db:dbSession, current_user:User|None = Depends(getCurrentUser)):

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    searched_post = db.scalar(select(Post).where(Post.post_id == post_id))

    if searched_post is None:
        raise HTTPException(detail="Post not found", status_code=status.HTTP_404_NOT_FOUND)

    try:
        comment = db.scalar(select(Comment).where(
            Comment.post_id == searched_post.post_id,
            Comment.comment_id == comment_id
        ))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to retrieve comment") from exc
    
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Comment not found on this post")
    
    return comment

# update existing comment only by the author of that comment
@router.put("/comments/{comment_id}", response_model=list[CommentUpdate])
def updateComment(comment_id:int, comment:CommentUpdate, db:dbSession, current_user:User|None = Depends(getCurrentUser)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        existing_comment = db.scalar(select(Comment).where(Comment.comment_id==comment_id))
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrieve the comment from database", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc

    if existing_comment is None:
        raise HTTPException(detail="Comment not found", status_code=status.HTTP_404_NOT_FOUND)

    if existing_comment.user_id != current_user.user_id:
        raise HTTPException(detail="You are not allowed to update this post", status_code=status.HTTP_403_FORBIDDEN)

    updated_comment = comment.model_dump()

    for key,value in updated_comment.items():
        setattr(existing_comment,key,value)
    try:
        db.commit()
        db.refresh(existing_comment)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(detail="failed to update the comment", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc


    return JSONResponse(content="Comment updated Successfully", status_code=status.HTTP_200_OK)


    # for existing_comment in COMMENTS:

    #     if existing_comment.get("comment_id") == comment_id:
    #         if user.get("user_id") != existing_comment.get("user_id"):
    #             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You does not have the permission to modify this post")

    #         # body = await request.json()
    #         updated_comment = comment.model_dump()
    #         existing_comment.update(updated_comment)

    #         return JSONResponse(content="Comment updated successfully", status_code=status.HTTP_200_OK)
    # return JSONResponse(content="Comment not exists", status_code=status.HTTP_404_NOT_FOUND)


# delete a comment 
@router.delete("/comments/{comment_id}")
def deleteComment(comment_id:int,db:dbSession, current_user:User|None = Depends(getCurrentUser)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    try:
        comment = db.scalar(select(Comment).where(Comment.comment_id==comment_id))
    except SQLAlchemyError as exc:
        raise HTTPException(detail="Failed to retrieve comments", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc

    if comment is None:
        raise HTTPException(detail="Comment not found", status_code=status.HTTP_404_NOT_FOUND)

    if comment.user_id != current_user.user_id:
        raise HTTPException(detail="You are not allowed to delete this post", status_code=status.HTTP_403_FORBIDDEN)

    try:
        db.delete(comment)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(detail="Database failed to delete the post",status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)from exc
        
    return JSONResponse(content="Comment deleted successfully", status_code=status.HTTP_200_OK) 
