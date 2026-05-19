from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str
    database_url: str
    port: int = 8000
    db_pool_size: int = 10
    dev_mode: bool = False


settings = Settings()
