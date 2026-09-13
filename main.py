from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI()

users = [
    {
        "user_id": 1,
        "username": "sakshi",
        "password": "sakshi123"
    },
    {
        "user_id": 2,
        "username": "vaishnavi",
        "password": "vaishnavi123"
    },
    {
        "user_id": 3,
        "username": "priya",
        "password": "priya123"
    },
    {
        "user_id": 4,
        "username": "neha",
        "password": "neha123"
    },
    {
        "user_id": 5,
        "username": "rohan",
        "password": "rohan123"
    }
]

posts = [
    {
        "post_id": 1,
        "user_id": 1,
        "content": "FastAPI is a framework of python"
    },
    {
        "post_id": 2,
        "user_id": 1,
        "content": "Flask is a framework of python"
    },

    {
        "post_id": 3,
        "user_id": 2,
        "content": "Swimming is better than hiking"
    },
    {
        "post_id": 4,
        "user_id": 2,
        "content": "Sun is rising"
    },
    {
        "post_id": 5,
        "user_id": 2,
        "content": "Reading books improves knowledge"
    },

    {
        "post_id": 6,
        "user_id": 3,
        "content": "Python is easy to learn"
    },
    {
        "post_id": 7,
        "user_id": 3,
        "content": "Coding requires regular practice"
    },
    {
        "post_id": 8,
        "user_id": 3,
        "content": "APIs help applications communicate"
    },

    {
        "post_id": 9,
        "user_id": 4,
        "content": "Exercise keeps our body healthy"
    },
    {
        "post_id": 10,
        "user_id": 4,
        "content": "Walking is good for health"
    },
    {
        "post_id": 11,
        "user_id": 4,
        "content": "Drinking enough water is important"
    },

    {
        "post_id": 12,
        "user_id": 5,
        "content": "Docker makes application deployment easier"
    },
    {
        "post_id": 13,
        "user_id": 5,
        "content": "Git is useful for version control"
    },
    {
        "post_id": 14,
        "user_id": 5,
        "content": "Linux is widely used by developers"
    }
]

comments = [
    {
        "comment_id": 101,
        "post_id": 1,
        "comment_content": "Good Information"
    },
    {
        "comment_id": 102,
        "post_id": 2,
        "comment_content": "Helpful"
    },
    {
        "comment_id": 103,
        "post_id": 3,
        "comment_content": "Yes, You are right"
    },
    {
        "comment_id": 104,
        "post_id": 4,
        "comment_content": "Wow"
    },
    {
        "comment_id": 105,
        "post_id": 5,
        "comment_content": "Absolutely"
    },
    {
        "comment_id": 106,
        "post_id": 6,
        "comment_content": "I agree"
    },
    {
        "comment_id": 107,
        "post_id": 7,
        "comment_content": "Very true"
    },
    {
        "comment_id": 108,
        "post_id": 8,
        "comment_content": "Nice explanation"
    },
    {
        "comment_id": 109,
        "post_id": 9,
        "comment_content": "That's true"
    },
    {
        "comment_id": 110,
        "post_id": 10,
        "comment_content": "I walk every day"
    },
    {
        "comment_id": 111,
        "post_id": 11,
        "comment_content": "Good reminder"
    },
    {
        "comment_id": 112,
        "post_id": 12,
        "comment_content": "Very useful"
    },
    {
        "comment_id": 113,
        "post_id": 13,
        "comment_content": "Yes, Git is important"
    },
    {
        "comment_id": 114,
        "post_id": 14,
        "comment_content": "Absolutely"
    }
]

# for user in users:
#     if user["user_id"] == 1:
#         print(type(user["posts"]))


class commentSchema(BaseModel):
    comment_id:int
    comment_content:str

class postSchema(BaseModel):
    post_id:int
    content:str
    comment:commentSchema
  
class requestSchema(BaseModel):
    user_id:int
    username:str
    password:str = Field(min_length=5)
    posts:postSchema

class responseSchema(BaseModel):
    user_id:int
    username:str
    posts:postSchema

# API : create new user
@app.post("/users")
def create_user(user:requestSchema):
    new_user = user.model_dump()
     
    for user in users:
        if user["user_id"] == user.user_id:
            return {"message" : "User already exists"}
        
    users.append(new_user)
    return new_user



# Task : get all users
@app.get("/users")
def get_all_posts():
    return users

# Task : get specific user by its id
@app.get("/users/{id}")
def get_user(id:int):
    for user in users:
        if user["user_id"]==id:
            return user
    return JSONResponse(content={"error": "User not found"}, status_code=status.HTTP_404_NOT_FOUND)
