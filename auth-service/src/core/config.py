
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

logging_config.dictConfig(LOGGING)


class FastapiConfig(BaseSettings):
    fastapi_project_name: str
    auth_host: str
    auth_port: int
    jwt_secret_key: str
    jwt_algorithm: str
    access_jwt_expire_minutes: int = 1
    refresh_jwt_expire_minutes: int = 30
    is_debug: bool
    tracer_enabled: bool = False
    limiter_enabled: bool = False
    tracer_host: str
    tracer_port: int

    model_config = SettingsConfigDict(
        env_file=".env_auth_fastapi", env_file_encoding='utf-8')


class PostgresConfig(BaseSettings):
    db_name: str
    db_user: str
    db_password: str
    db_port: str
    db_host: str
    db_dsn: PostgresDsn

    model_config = SettingsConfigDict(env_file=".env_auth_db", env_file_encoding='utf-8')


class RedisConfig(BaseSettings):
    redis_host: str
    redis_port: str

    model_config = SettingsConfigDict(env_file=".env_redis", env_file_encoding='utf-8')


class YandexAuthConfig(BaseSettings):
    client_id: str
    client_secret: str
    redirect_uri: str

    model_config = SettingsConfigDict(
        env_file=".env_auth_ya", env_file_encoding='utf-8')


class ExternalAuth(BaseSettings):
    OAUTH_CREDENTIALS: dict


class MailGateApi:
    host: str
    port: int

    model_config = SettingsConfigDict(
        env_file=".env_mail_gate", env_file_encoding='utf-8')


class RabbitMQConfig(BaseSettings):
    host: str
    queue_ready: str
    user: str
    password: str
    exchange_name: str
    routing_key: str

    model_config = SettingsConfigDict(
        env_file=".env_rabbitmq", env_file_encoding='utf-8')


postgres_config = PostgresConfig()
rabbitmq_config = RabbitMQConfig()



fastapi_config = FastapiConfig()
postgres_config = PostgresConfig()
redis_config = RedisConfig()
yandex_auth_config = YandexAuthConfig()

external_auth = {}
external_auth['OAUTH_CREDENTIALS']={'yandex': yandex_auth_config.model_dump()}