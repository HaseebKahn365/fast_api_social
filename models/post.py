from pydantic import BaseModel
from typing import List


class Comment(BaseModel):
    id: int
    content: str
    post_id: int


class Post(BaseModel):
    id: int
    title: str
    comments: List[Comment] = []


class CommentIn(BaseModel):
    content: str


class PostCreate(BaseModel):
    title: str


# In-memory sample data
posts: dict[int, Post] = {
    1: Post(id=1, title="Post 1",
            comments=[
                Comment(id=1, content="Great post!", post_id=1),
                Comment(id=2, content="Thanks for sharing.", post_id=1)
            ]),
    2: Post(id=2, title="Post 2", comments=[]),
}
