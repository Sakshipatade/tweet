from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


users = [
    {
        "user_id": 1,
        "username": "sakshi",
        "password": "sakshi123",
        "posts": [
            {
                "post_id": 1,
                "content": "FastAPI is a framework of python",
                "comment": {
                    "comment_id": 101,
                    "comment_content": "Good Information"
                }
            },
            {
                "post_id": 2,
                "content": "Flask is a framework of python",
                "comment": {
                    "comment_id": 102,
                    "comment_content": "Helpful"
                }
            }
        ]
    },
    {
        "user_id": 2,
        "username": "vaishnavi",
        "password": "vaishnavi123",
        "posts": [
            {
                "post_id": 1,
                "content": "Swimming is better than hiking",
                "comment": {
                    "comment_id": 103,
                    "comment_content": "Yes, You are right"
                }
            },
            {
                "post_id": 2,
                "content": "Sun is rising",
                "comment": {
                    "comment_id": 104,
                    "comment_content": "Wow"
                }
            },
            {
                "post_id": 3,
                "content": "Reading books improves knowledge",
                "comment": {
                    "comment_id": 105,
                    "comment_content": "Absolutely"
                }
            }
        ]
    },
    {
        "user_id": 3,
        "username": "priya",
        "password": "priya123",
        "posts": [
            {
                "post_id": 1,
                "content": "Python is easy to learn",
                "comment": {
                    "comment_id": 106,
                    "comment_content": "I agree"
                }
            },
            {
                "post_id": 2,
                "content": "Coding requires regular practice",
                "comment": {
                    "comment_id": 107,
                    "comment_content": "Very true"
                }
            },
            {
                "post_id": 3,
                "content": "APIs help applications communicate",
                "comment": {
                    "comment_id": 108,
                    "comment_content": "Nice explanation"
                }
            }
        ]
    },
    {
        "user_id": 4,
        "username": "neha",
        "password": "neha123",
        "posts": [
            {
                "post_id": 1,
                "content": "Exercise keeps our body healthy",
                "comment": {
                    "comment_id": 109,
                    "comment_content": "That's true"
                }
            },
            {
                "post_id": 2,
                "content": "Walking is good for health",
                "comment": {
                    "comment_id": 110,
                    "comment_content": "I walk every day"
                }
            },
            {
                "post_id": 3,
                "content": "Drinking enough water is important",
                "comment": {
                    "comment_id": 111,
                    "comment_content": "Good reminder"
                }
            }
        ]
    },
    {
        "user_id": 5,
        "username": "rohan",
        "password": "rohan123",
        "posts": [
            {
                "post_id": 1,
                "content": "Docker makes application deployment easier",
                "comment": {
                    "comment_id": 112,
                    "comment_content": "Very useful"
                }
            },
            {
                "post_id": 2,
                "content": "Git is useful for version control",
                "comment": {
                    "comment_id": 113,
                    "comment_content": "Yes, Git is important"
                }
            },
            {
                "post_id": 3,
                "content": "Linux is widely used by developers",
                "comment": {
                    "comment_id": 114,
                    "comment_content": "Absolutely"
                }
            }
        ]
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

# # API : create new user
# @app.post("/users")
# def create_user(user:requestSchema):
#     new_user = user.model_dump()
     
#     for user in users:
#         if user["user_id"] == user.user_id:
#             return {"message" : "User already exists"}
        
#     users.append(new_user)
#     return new_user



# Task : get all users
@app.get("/users")
def get_all_posts():
    return users

