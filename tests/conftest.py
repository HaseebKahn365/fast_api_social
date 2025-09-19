from typing import AsyncGenerator, Generator
import os

import pytest

os.environ["ENV_STATE"] = "test"
from fastapi.testclient import TestClient
from httpx import AsyncClient
from httpx import ASGITransport

from database import database

from main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def client() -> Generator:
    print("Setting up TestClient")
    yield TestClient(app)

@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture
async def async_client() -> AsyncGenerator:
    # use ASGITransport so httpx AsyncClient works with FastAPI app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac



        