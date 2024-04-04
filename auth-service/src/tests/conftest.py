from core.config import postgres_config
from pydantic_core import MultiHostUrl


def override_db_name():
    """Prefix database name with test_"""
    uri = str(postgres_config.db_dsn)

    uri = uri + '_test'
    postgres_config.db_dsn = MultiHostUrl(uri)


override_db_name()


pytest_plugins = [
    "tests.fixtures.db",
    "tests.fixtures.client",
    "tests.fixtures.data",
]
