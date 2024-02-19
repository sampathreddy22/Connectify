from fastapi import APIRouter, HTTPException

from connectify.database import comment_table, database, post_table
from connectify.models.post import (
    Comment,
    CommentIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
)

router = APIRouter()


async def find_post_by_id(post_id: int):
    """
    Find a post by its id.

    Args:
        post_id (int): The id of the post.

    Returns:
        dict: The post with the given id.
    """
    query = (
        post_table.select().where(post_table.c.id == post_id)
        if post_table is not None
        else None
    )
    return await database.fetch_one(query)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    """
    Create a new post.

    Args:
        post (UserPostIn): The post data.

    Returns:
        dict: The newly created post.
    """
    data = post.model_dump()
    query = post_table.insert().values(data) if post_table is not None else None
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    """
    Create a new comment.

    Args:
        comment (CommentIn): The comment data.

    Returns:
        dict: The newly created comment.
    """
    post = await find_post_by_id(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    data = comment.model_dump()
    query = comment_table.insert().values(data) if comment_table is not None else None
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post", response_model=list[UserPost])
async def get_posts():
    """
    Get all posts.

    Returns:
        list: The list of posts.
    """
    query = post_table.select() if post_table is not None else None
    return await database.fetch_all(query)


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_post(post_id: int):
    """
    Get all comments for a post.

    Args:
        post_id (int): The id of the post.

    Returns:
        list: The list of comments for the post.
    """
    query = (
        comment_table.select().where(comment_table.c.post_id == post_id)
        if comment_table is not None
        else None
    )
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    """
    Get a post with its comments.

    Args:
        post_id (int): The id of the post.

    Returns:
        dict: The post with its comments.
    """
    post = await find_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "post": post,
        "comments": await get_comments_post(post_id),
    }
