from config import postgres_config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base


engine = create_async_engine(postgres_config.db_dsn.unicode_string(),
                             echo=True,
                             future=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False,
)

Base = declarative_base()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def create_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
