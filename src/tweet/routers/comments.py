from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from tweet.data import USERS,POSTS, COMMENTS, TOKENS

router = APIRouter()


# get all comments only after user is loggedIn
@router.get("/comments")
def getAllComments(request:Request):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    return COMMENTS

# get comments written by me OR current loggedIn user
@router.get("/comments/me")
def getMyComments(request:Request):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    all_comments = []
    for comment in COMMENTS:
        if comment.get("user_id") == user.get("user_id"):
            all_comments.append(comment)
    return all_comments


# get all comments on my all posts
@router.get("/me/comments/received")
def getCommentsOnMyPosts(request:Request):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    all_comments = []

    for post in POSTS:
        if user.get("user_id") == post.get("user_id"):
            for comment in COMMENTS:
                if post.get("post_id") == comment.get("post_id"):
                    all_comments.append(comment)
    return all_comments



# get all comments on my specific posts
@router.get("/me/posts/{post_id}/comments")
def getAllCommentsOnMyPost(request:Request, post_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    all_comments = []
    for post in POSTS:
        if post.get("user_id") == user.get("user_id") and post.get("post_id") == post_id:
            for comment in COMMENTS:
                if comment.get("post_id") == post_id:
                    all_comments.append(comment)
            return all_comments
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found..")