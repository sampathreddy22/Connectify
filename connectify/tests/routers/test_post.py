import pytest
from httpx import AsyncClient


async def create_post(body: str, async_client: AsyncClient):
    response = await async_client.post("/api/v1/post", json={"body": body})
    return response.json()


async def create_comment(post_id: int, body: str, async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/comment", json={"post_id": post_id, "body": body}
    )
    return response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient):
    return await create_post("Test post", async_client)


@pytest.fixture()
async def created_comment(async_client: AsyncClient, created_post: dict):
    return await create_comment(created_post["id"], "Test comment", async_client)


@pytest.mark.anyio
async def test_create_post(async_client: AsyncClient):
    body = "Test post"
    response = await async_client.post(
        "/api/v1/post",  # Updated URL path
        json={"body": body},
    )

    assert response.status_code == 201
    assert {"id": 1, "body": body}.items() <= response.json().items()


@pytest.mark.anyio
async def test_create_post_with_nobody(async_client: AsyncClient):
    response = await async_client.post("/api/v1/post", json={})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/api/v1/post")
    assert response.status_code == 200
    assert response.json() == [created_post]


@pytest.mark.anyio
async def test_create_comment(async_client: AsyncClient, created_post: dict):
    response = await async_client.post(
        "/api/v1/comment",
        json={"post_id": created_post["id"], "body": "Test comment"},
    )
    assert response.status_code == 201
    assert {
        "id": 1,
        "post_id": created_post["id"],
        "body": "Test comment",
    }.items() <= response.json().items()


@pytest.mark.anyio
async def test_get_comments_on_post(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/api/v1/post/{created_post['id']}/comment")
    assert response.status_code == 200
    assert response.json() == [created_comment]


@pytest.mark.anyio
async def test_get_commnets_on_post_empty(
    async_client: AsyncClient, created_post: dict
):
    response = await async_client.get(f"/api/v1/post/{created_post['id']}/comment")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_get_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/api/v1/post/{created_post['id']}")
    assert response.status_code == 200
    assert response.json() == {"post": created_post, "comments": [created_comment]}


@pytest.mark.anyio
async def test_get_missing_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get("/api/v1/post/5")
    assert response.status_code == 404
    assert response.json() == {"detail": "Post not found"}
