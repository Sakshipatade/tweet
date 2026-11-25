from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PostCreate(BaseModel):
    content:str 

class PostUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content:str

class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True) #reads value from SQLAlchemy objects
    post_id:int
    user_id:int
    content:str
    created_at:datetime
    updated_at:datetime