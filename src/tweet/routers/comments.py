from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from tweet.data import USERS,POSTS, COMMENTS, TOKENS
from tweet.routers.auth import getCurrentUser

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


# get a single comment 
@router.get("/comments/{id}")
def getSpecificComment(request:Request, id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    for comment in COMMENTS:
        if comment.get("comment_id") == id:
            return comment
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found..")


# get comments written by a specific user
@router.get("/users/{user_id}/comments")
def getCommentsByUser(request:Request, user_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    requested_user = None

    for user in USERS:
        if user.get("user_id") == user_id:
            requested_user = user
            break

    if requested_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found..")

    
    user_comments = []
    for comment in COMMENTS:
        if comment.get("user_id") == user_id:
            user_comments.append(comment)
    return user_comments



# get a specific comment written by that user
@router.get("/users/{user_id}/comments/{comment_id}")
def getSpecificCommentOfUser(request:Request, user_id:int, comment_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    requested_user = None

    for user in USERS:
        if user.get("user_id") == user_id:
            requested_user = user
            break

    if requested_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found..")

    for comment in COMMENTS:
        if comment.get("user_id") == user_id and comment.get("comment_id") == comment_id:
            return comment
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found..")


# get all comments on any specific posts 
@router.get("/posts/{post_id}/comments")
def getAllCommentsOnAnyPost(request:Request, post_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    
    for post in POSTS:
        if post.get("post_id") == post_id:
            all_comments = []
            for comment in COMMENTS:
                if comment.get("post_id") == post_id:
                    all_comments.append(comment)
            return all_comments
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found..")


# get specific comment on a specific post
@router.get("/posts/{post_id}/comments/{comment_id}")
def getSpecificCommentOfSpecificPost(request:Request, post_id:int, comment_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    post_exists = False

    for post in POSTS:
        if post.get("post_id") == post_id:
            post_exists = True
            break

    if not post_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found..")

    for comment in COMMENTS:
        if comment.get("comment_id") == comment_id and comment.get("post_id") == post_id:
            return comment
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found..")


# TODO: add security
# create a new comment 
@router.post("/comments")
async def createComment(request:Request):
    user = getCurrentUser(request)

    if user is None:
        # return JSONResponse(content="You are unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    body = await request.json()

    post_id = body.get("post_id")
    if post_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post Id is Required")

    # check whether the post exists
    # post_exits = False
    # for post in POSTS:
    #     if post.get("post_id") == post_id:
    #         post_exits = True
    #         break
    # OR
    post_exists = any(post.get("post_id") == post_id for post in POSTS)

    if not post_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found..")

    # generate new comment id
    new_comment_id = max(comment.get("comment_id") for comment in COMMENTS)+1

    # set the author and the comment id on the server
    body["user_id"] = user.get("user_id")
    body["comment_id"] = new_comment_id

    COMMENTS.append(body)

    return JSONResponse(content="comment added successfully", status_code=status.HTTP_201_CREATED)


# update existing comment only by the author of that comment
@router.put("/comments/{comment_id}")
async def updateComment(request:Request, comment_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    for comment in COMMENTS:

        if comment.get("comment_id") == comment_id:
            if user.get("user_id") != comment.get("user_id"):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You does not have the permission to modify this post")

            body = await request.json()

            # We write these lines to prevent the user from changing the Comment Id or the owner of the post through the request body.
            body.pop("comment_id", None)
            body.pop("user_id", None)
            body.pop("post_id",None)

            comment.update(body)

            return JSONResponse(content="Comment updated successfully", status_code=status.HTTP_200_OK)
    return JSONResponse(content="Comment not exists", status_code=status.HTTP_404_NOT_FOUND)


# delete a comment 
@router.delete("/comments/{comment_id}")
def deleteComment(request:Request, comment_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    for comment in COMMENTS:
        if comment.get("comment_id") == comment_id:
            if comment.get("user_id") == user.get("user_id"):
                COMMENTS.remove(comment)
                return JSONResponse(content="Comment Deleted..", status_code=status.HTTP_200_OK)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You does not have the permission to delete this post")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
