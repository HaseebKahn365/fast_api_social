import pytest
from httpx import AsyncClient

async def create_post(body: str, async_client) -> dict:
    response = await async_client.post("/posts", json={"title": body})
    assert response.status_code == 201
    return response.json()


async def create_comment(post_id: int, content: str, async_client) -> dict:
    response = await async_client.post(f"/posts/{post_id}/comments", json={"content": content})
    assert response.status_code == 200
    return response.json()

@pytest.fixture()
async def created_post(async_client: AsyncClient) -> dict:
    return await create_post("Test Post", async_client)


@pytest.fixture()
async def created_comment(created_post: dict, async_client: AsyncClient, tester : str = "Haseeb") -> dict:
    print("Tested by ", tester)
    return await create_comment(created_post["id"], "Test Comment", async_client)

@pytest.mark.anyio
async def test_create_post(async_client: AsyncClient):
    body = "Test Post"
    response = await async_client.post("/posts", json={"title": body})
    assert response.status_code == 201
    
    assert {
        "id": response.json()["id"],
        "title": body,
        "comments": []
    }.items() <= response.json().items()





@pytest.mark.anyio
async def test_create_post_missing_data(async_client: AsyncClient):
    response = await async_client.post("/posts", json={})
    assert response.status_code == 422  # Unprocessable Entity for missing required fields


@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/posts")
    assert response.status_code == 200
    assert response.json()  == [created_post] or len(response.json()) >= 1

@pytest.mark.anyio
async def test_create_comment(async_client: AsyncClient, created_post: dict):
    content = "Nice post!"
    response = await async_client.post(f"/posts/{created_post['id']}/comments", json={"content": content})
    assert response.status_code == 200
    assert {
        "id": response.json()["id"],
        "content": content,
        "post_id": created_post["id"]
    }.items() <= response.json().items()


@pytest.mark.anyio
async def test_get_comments_on_post(async_client: AsyncClient, created_post: dict, created_comment: dict):
    response = await async_client.get(f"/posts/{created_post['id']}")
    assert response.status_code == 200
    assert {
        "id": created_post["id"],
        "title": created_post["title"],
        "comments": [created_comment]
    }.items() <= response.json().items()

@pytest.mark.anyio
async def test_get_post_with_comments(async_client: AsyncClient, created_post: dict, created_comment: dict):
    response = await async_client.get(f"/posts/{created_post['id']}")
    assert response.status_code == 200
    assert {
        "id": created_post["id"],
        "title": created_post["title"],
        "comments": [created_comment]
    }.items() <= response.json().items()
