from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    DATABASE_URL: str = "postgresql+psycopg://rag_user:rag_password@localhost:5432/rag_db"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
