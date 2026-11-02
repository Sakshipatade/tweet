from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import JSONResponse
from tweet.data import USERS,POSTS, COMMENTS, TOKENS

router = APIRouter()



# getting all posts of specified user
@router.get("/users/{user_id}/posts")
def getUserPosts(request:Request, user_id:int):
    user = getCurrentUser(request)
    print("Current User: ", user)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    
    user_posts = []
    for post in POSTS:
        if post.get("user_id") == user_id:
            user_posts.append(post)
    return user_posts



# getting all posts of specified user
@router.get("/users/{user_id}/posts")
def getUserPosts(request:Request, user_id:int):
    user = getCurrentUser(request)
    print("Current User: ", user)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")
    
    user_posts = []
    for post in POSTS:
        if post.get("user_id") == user_id:
            user_posts.append(post)
    return user_posts


# deleting post of the user who is loggedIn
@router.delete("/posts/{id}")
def deletePost(request:Request, id:int):
    user = getCurrentUser(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    for post in POSTS:
        if post.get("post_id") == id:
            if post.get("user_id") == user.get("user_id"):
                POSTS.remove(post)
                return JSONResponse(content="Post deleted successfully.", status_code=status.HTTP_200_OK)
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You does have the permission to delete this post..")



# create a new post by the user who is loggedIn
@router.post("/posts")
async def createPost(request:Request):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    # data =  await request.body()
    # body = json.loads(data)
    body = await request.json()

    new_post_id = max(post.get("post_id") for post in POSTS) + 1

    body["user_id"] = user.get("user_id")
    body["post_id"] = new_post_id
    POSTS.append(body)
    return JSONResponse(content="Post created successfully..", status_code=status.HTTP_201_CREATED)


# update the post of the user by himself only after he is loggedIn
@router.put("/posts/{post_id}")
async def updatePost(request:Request, post_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    for post in POSTS:
        if post.get("post_id") == post_id:

            if post.get("user_id") != user.get("user_id"):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You does not have the permission to modify this post")


            body = await request.json()

            # We write these two lines to prevent the user from changing the post ID or the owner of the post through the request body.
            body.pop("post_id", None)
            body.pop("user_id", None)

            post.update(body)
            return JSONResponse(content="Post updated sucessfully..", status_code=status.HTTP_200_OK)
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found..")


# get all posts on which i have commented or loggedIn user commented
@router.get("/me/commented_posts")
def getPostsOnUserCommented(request:Request):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")

    all_posts = []
    for comment in COMMENTS:
        if comment.get("user_id") == user.get("user_id"):
            for post in POSTS:
                if post.get("post_id") == comment.get("post_id"):
                    if post not in all_posts:
                        all_posts.append(post)

    return all_posts



# get specific post which i have commmented
@router.get("/me/commented_posts/{post_id}")
def getPostOnICommented(request:Request, post_id:int):
    user = getCurrentUser(request)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "User is Unauthorized")


    for comment in COMMENTS:
        if comment.get("user_id") == user.get("user_id") and comment.get("post_id") == post_id:
            for post in POSTS:
                if post_id == post.get("post_id"):
                    return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found or You are not commented on the post")