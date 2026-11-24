from pydantic import BaseModel, ConfigDict

class CommentCreate(BaseModel):
    post_id:int
    comment_content:str

class CommentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    comment_content:str

class CommentResponse(BaseModel):
    comment_id:int
    user_id:int
    post_id:int
    comment_content:str