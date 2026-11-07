from pydantic import BaseModel,ConfigDict

class UserCreate(BaseModel):
    username:str
    password:str

class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")  #rejects any extra or unexpected fields passed to a data model.
    username:str
    password:str


class UserPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username:str | None = None
    password:str | None = None


class UserResponse(BaseModel):
    user_id:int
    username:str


class UserPriviledgeResponse(BaseModel):
    user_id:int
    username:str
    password:str