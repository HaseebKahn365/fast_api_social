from fastapi import APIRouter, HTTPException
from models.post import Post, Comment, CommentIn, PostCreate, posts

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("")
async def list_posts():
    return list(posts.values())


@router.post("")
async def create_post(post_data: PostCreate):
    post_id = len(posts) + 1
    posts[post_id] = Post(id=post_id, title=post_data.title)
    return posts[post_id]


@router.get("/{post_id}")
async def get_post(post_id: int):
    post = posts.get(post_id)
    if post:
        return post
    raise HTTPException(status_code=404, detail="Post not found")


@router.post("/{post_id}/comments")
async def add_comment(post_id: int, comment_data: CommentIn):
    post = posts.get(post_id)
    if post:
        comment_id = len(post.comments) + 1
        comment = Comment(id=comment_id, content=comment_data.content, post_id=post_id)
        post.comments.append(comment)
        return comment
    raise HTTPException(status_code=404, detail="Post not found")