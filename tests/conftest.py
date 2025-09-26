from typing import AsyncGenerator, Generator
import os

import pytest

os.environ["ENV_STATE"] = "test"
from fastapi.testclient import TestClient
from httpx import AsyncClient
from httpx import ASGITransport

from database import database, user_table

from main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    print("Setting up TestClient")
    yield TestClient(app)

@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()

@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@example.net", "password": "1234"}
    response = await async_client.post("/users/register", json=user_details)
    
    # CRITICAL: Fail if registration fails
    assert response.status_code == 200, f"Registration failed: {response.json()}"
    
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    
    # CRITICAL: Fail if user is not found in DB
    assert user is not None, "User registered but not found in database."
    
    user_details["id"] = user["id"]
    return user_details

@pytest.fixture()
async def async_client() -> AsyncGenerator:
    # use ASGITransport so httpx AsyncClient works with FastAPI app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac



