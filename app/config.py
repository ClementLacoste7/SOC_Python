from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    secret_key: str
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./incidents.db"
    log_level: str = "INFO"


settings = Settings()
