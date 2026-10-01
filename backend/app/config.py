from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./phishing_analyzer.db"
    api_key: str = "changeme-local-dev-key"


settings = Settings()
