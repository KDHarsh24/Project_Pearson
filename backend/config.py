from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Core
    environment: str = "dev"
    db_url: str = "sqlite:///./app.db"
    vector_db_path: str = "legal_cases_store"
    case_law_collection: str = "legal_cases"
    case_files_collection: str = "case_files"

    # IBM / WatsonX
    watsonx_api_key: str | None = None
    watsonx_project_id: str | None = None
    watsonx_url: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
