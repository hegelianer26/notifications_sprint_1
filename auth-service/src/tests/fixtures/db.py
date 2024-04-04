from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from core.config import postgres_config
from db.sql.database import Base, get_session
from main import app
from sqlalchemy import create_engine, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, SessionTransaction


@pytest.fixture(scope="session", autouse=True)
def setup_test_db() -> Generator:
    engine = create_engine(str(postgres_config.db_dsn).replace('+asyncpg', ''))

    with engine.begin():
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        yield
        Base.metadata.drop_all(engine)


@pytest_asyncio.fixture(autouse=True)
async def session() -> AsyncGenerator:
    # https://github.com/sqlalchemy/sqlalchemy/issues/5811#issuecomment-756269881
    async_engine = create_async_engine(str(postgres_config.db_dsn))
    async with async_engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()
        async_session_factory = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=conn,
        )

        async_session = async_session_factory()

        @event.listens_for(async_session.sync_session, "after_transaction_end")
        def end_savepoint(_session: Session, _transaction: SessionTransaction) -> None:
            if conn.closed:
                return
            if not conn.in_nested_transaction():
                if conn.sync_connection:
                    conn.sync_connection.begin_nested()

        def test_get_session() -> Generator:
            try:
                yield async_session_factory()
            except SQLAlchemyError:
                pass

        app.dependency_overrides[get_session] = test_get_session

        yield async_session
        await async_session.close()
        await conn.rollback()

