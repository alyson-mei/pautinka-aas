from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):

    PROJECT_NAME: str = "Pautinka as a Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1" # API version prefix for all endpoints

    DATABASE_URL: str = "sqlite+aiosqlite:///./pautinka.db"

    # CORS (Cross-Origin Resource Sharing) configuration
    # Allows these origins to make requests to our API from browsers
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Common React development server
        "http://localhost:8080"   # Common Vue.js development server
    ]
    
    TELEGRAM_API_ID: Optional[int] = None
    TELEGRAM_API_HASH: Optional[str] = None

    CHANNEL_USERNAME: str = "MyKittyPautinka"
    SESSION_PATH: str = "sessions/pautinka"
    IMAGE_PATH: str = "static/images"
    TEXT_PATH: str = "static/texts"
    DOWNLOAD_LIMIT: int = 250

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

if __name__ == '__main__':
    try:
        settings.TELEGRAM_API_ID
        settings.TELEGRAM_API_HASH
    except Exception as e:
        print(e)

