from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from httpx import ASGITransport


from main import app
from models.post import posts

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def client() -> Generator:
    print("Setting up TestClient")
    yield TestClient(app)

@pytest.fixture(autouse=True)
def db():
    """Synchronous autouse fixture to reset in-memory posts between tests."""
    print("Setting up DB")
    posts.clear()  # Clear the in-memory posts before each test
    yield


@pytest.fixture
async def async_client() -> AsyncGenerator:
    # use ASGITransport so httpx AsyncClient works with FastAPI app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac



        