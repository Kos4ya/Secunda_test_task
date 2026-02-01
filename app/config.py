from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/organizations_db"
    API_KEY: str = "your-secret-api-key-here"
    PROJECT_NAME: str = "Organizations Directory API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    DEFAULT_SEARCH_RADIUS: float = 1000.0

    MAX_ACTIVITY_LEVEL: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()