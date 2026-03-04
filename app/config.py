from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "news_db"
    
    NEWS_API_KEY: str = ""
    
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    @property
    def DATABASE_URL(self) -> str:
        # Using synchronous pymysql for Celery compatibility if needed, or aiomysql for FastAPI.
        # We will use pymysql to keep it simple and compatible with both FastAPI and Celery.
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
