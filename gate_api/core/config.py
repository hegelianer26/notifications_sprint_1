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


class FastapiConfig(BaseSettings):
    fastapi_project_name: str
    is_debug: bool
    tracer_enabled: bool = False
    limiter_enabled: bool = False
    tracer_host: str
    tracer_port: int

    model_config = SettingsConfigDict(
        env_file=".env_gate_fastapi", env_file_encoding='utf-8')


class RabbitMQConfig(BaseSettings):
    host: str
    queue_draft: str
    user: str
    password: str
    exchange_name: str
    routing_key: str

    model_config = SettingsConfigDict(
        env_file=".env_rabbitmq", env_file_encoding='utf-8')


rabbitmq_config = RabbitMQConfig()
fastapi_config = FastapiConfig()
postgres_config = PostgresConfig()