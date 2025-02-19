import os
import pytest_asyncio
import pytest
from dotenv import load_dotenv

from database.db import Base

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool


load_dotenv(".test.env")
ASYNC_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
async_engine = create_async_engine(ASYNC_DATABASE_URL, poolclass=NullPool)

DATABASE_URL = os.getenv("TEST_DATABASE")
engine = create_engine(DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@pytest_asyncio.fixture(scope="function")
async def session():
    async with async_engine.connect() as connection:
        transaction = await connection.begin_nested()
        session = AsyncSession(
            bind=connection, join_transaction_mode="create_savepoint"
        )
        yield session
        await session.close()
        await transaction.rollback()
        await connection.close()
