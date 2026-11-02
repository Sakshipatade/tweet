from pydantic import BaseModel,ConfigDict

class UserCreate(BaseModel):
    username:str
    password:str

class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")  #rejects any extra or unexpected fields passed to a data model.
    username:str
    password:str

class UserResponse(BaseModel):
    user_id:int
    username:str