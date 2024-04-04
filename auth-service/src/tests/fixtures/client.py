import pytest_asyncio
from httpx import AsyncClient
from main import app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
