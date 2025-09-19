from fastapi import APIRouter, HTTPException

from models.post import (Post, Comment, CommentIn, PostIn)

from database import post_table, comment_table, database

router = APIRouter()


#find post

async def find_post(post_id: int):
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)

#get all posts
@router.get("/post", response_model=list[Post])
async def get_all_posts() -> list[Post]:
    query = post_table.select()
    posts = await database.fetch_all(query)
    # Add empty comments list to each post for consistency
    return [{"id": post["id"], "title": post["title"], "comments": []} for post in posts]

# Create a new post
@router.post("/post", response_model=Post, status_code=201)
async def create_post(post: PostIn):
    data = post.model_dump()
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id, "comments": []}

# Get a single post by ID
@router.get("/{post_id}", response_model=Post)
async def get_post(post_id: int):
    # Get the post
    post_query = post_table.select().where(post_table.c.id == post_id)
    post_result = await database.fetch_one(post_query)
    if post_result is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Get comments for this post
    comments_query = comment_table.select().where(comment_table.c.post_id == post_id)
    comments_result = await database.fetch_all(comments_query)
    
    # Return post with comments
    return {
        "id": post_result["id"],
        "title": post_result["title"],
        "comments": comments_result
    }


# routes for comments

#create comment
@router.post("/{post_id}/comments", response_model=Comment, status_code=201)
async def create_comment(post_id: int, comment: CommentIn):
    data = comment.model_dump()
    data["post_id"] = post_id  # Add the post_id to the comment data
    query = comment_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


#get comments on a post
@router.get("/{post_id}/comments", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    return await database.fetch_all(query)