from pydantic import BaseModel, ConfigDict

class PostCreate(BaseModel):
    content:str 

class PostUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content:str

class PostResponse(BaseModel):
    post_id:int
    user_id:int
    content:str