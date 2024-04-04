import asyncio
from functools import wraps

import typer
import uvicorn
from alembic import command
from alembic.config import Config
from core.config import postgres_config
from db.sql.database import async_session
from db.sql.models import User

app = typer.Typer()


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


@app.command()
def migration():
    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', 'migrations')
    alembic_cfg.set_main_option(
        'sqlalchemy.url', postgres_config.db_dsn.unicode_string() + '?async_fallback=True')
    command.upgrade(alembic_cfg, 'head')
    command.revision(alembic_cfg, autogenerate=True)
    command.upgrade(alembic_cfg, 'head')



@app.command()
@coro
async def superuser():
    async with async_session() as session:
        username: str = input('введите имя пользователья: ')
        password: str = input('введите пароль: ')
        user_db = User(username=username, password=password)
        user_db.is_admin = True
        session.add(user_db)
        await session.commit()


@app.command()
def startapp():
    uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8081,
            reload=True
        )


if __name__ == "__main__":
    app()
