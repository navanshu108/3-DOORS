import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "3 DOORS"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./3doors.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-for-hackathon-demo")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

    class Config:
        env_file = ".env"
        extra = "ignore" # Ignore extra fields from old .env file

settings = Settings()
