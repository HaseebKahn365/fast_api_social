from pydantic import BaseModel
from typing import List


class Comment(BaseModel):
    id: int
    post_id: int
    content: str
    
    class Config:
        orm_mode = True


class Post(BaseModel):
    id: int
    title: str
    comments: List[Comment] = []
    
    class Config:
        orm_mode = True



class CommentIn(BaseModel):
    content: str


class PostIn(BaseModel):
    title: str


class PostInWithComments(PostIn):
    comments: List[Comment] = []