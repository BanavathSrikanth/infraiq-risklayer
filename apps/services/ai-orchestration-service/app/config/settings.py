from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "infraiq-ai-orchestration-service"
    environment: str = "development"
    model_provider: str = "local-deterministic"
    model_name: str = "proposal-engine"
    model_version: str = "1.0"
    foundry_endpoint: str | None = None
    document_intelligence_endpoint: str | None = None
    ai_search_endpoint: str | None = None
    vision_endpoint: str | None = None
    blob_connection_string: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_deployment: str = "gpt-4o-mini"
    mapping_store_path: str = ".data/mapping-proposals.json"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
