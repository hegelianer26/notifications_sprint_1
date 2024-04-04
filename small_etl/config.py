from pydantic_settings import BaseSettings, SettingsConfigDict


class FromPostgresConfig(BaseSettings):
    db_name: str
    db_user: str
    db_password: str
    db_port: str
    db_host: str

    model_config = SettingsConfigDict(
        env_file=".env_auth_db", env_file_encoding='utf-8')


class ToPostgresConfig(BaseSettings):
    db_name: str
    db_user: str
    db_password: str
    db_port: str
    db_host: str

    model_config = SettingsConfigDict(
        env_file=".env_postgres_db", env_file_encoding='utf-8')


from_config = FromPostgresConfig()
to_config = ToPostgresConfig()
