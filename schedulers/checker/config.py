from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresConfig(BaseSettings):
    db_name: str
    db_user: str
    db_password: str
    db_port: str
    db_host: str
    db_dsn: PostgresDsn

    model_config = SettingsConfigDict(
        env_file=".env_postgres_db", env_file_encoding='utf-8')


class RabbitMQConfig(BaseSettings):
    host: str
    queue: str
    user: str
    password: str
    exchange_name: str

    model_config = SettingsConfigDict(
        env_file=".env_rabbitmq", env_file_encoding='utf-8')


rabbitmq_config = RabbitMQConfig()
postgres_config = PostgresConfig()
