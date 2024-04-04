import pytest_asyncio
from db.sql.models import Role, User
from tests.fixtures.db import session


@pytest_asyncio.fixture(name="create_admin")
async def create_admin(session):
    user_admin = User(username="admin", password="admin")
    user_admin.is_admin = True
    session.add(user_admin)
    await session.commit()

@pytest_asyncio.fixture(name="create_not_admin")
async def create_not_admin(session):
    user_admin = User(username="notadmin", password="notadmin")
    session.add(user_admin)
    await session.commit()

@pytest_asyncio.fixture(name="create_role")
async def create_role(session):
    new_role = Role(
        name="the knight",
        description="warrior on horse",
        uuid="26acca1f-80eb-4cc4-a0de-2a160534f211")
    session.add(new_role)
    await session.commit()