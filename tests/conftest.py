from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
import pytest
from api.app import create_app
from cache.cache_client import RedisCache
from sqlalchemy.ext.asyncio import AsyncSession

from cache.dependencies import get_redis_cache
from db.base import get_session


@pytest.fixture(scope="session")
def mock_redis_cache():
    mock_cache = AsyncMock(spec=RedisCache)
    return mock_cache

@pytest.fixture(scope="session")
def mock_db_session():
    session = AsyncMock(spec=AsyncSession)
    return session

@pytest.fixture(scope="session")
def application():
    return create_app()

@pytest.fixture(scope="session")
def client(application, mock_redis_cache, mock_db_session):
    application.dependency_overrides[get_redis_cache] = lambda: mock_redis_cache
    application.dependency_overrides[get_session] = lambda: mock_db_session
    client = TestClient(application)
    return client
