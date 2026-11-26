from fastapi import FastAPI

from tweet.routers import users,posts,comments,auth

app = FastAPI()

app.include_router(users.router, tags=["Users"], prefix= "/users")
app.include_router(posts.router, tags=["Posts"])
app.include_router(comments.router, tags=["Comments"])
app.include_router(auth.router, tags=["Authentication"], prefix="/auth")
