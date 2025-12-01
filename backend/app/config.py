from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # azure openai stuff
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_chat_deployment: str
    azure_openai_embedding_deployment: str

    # search config
    azure_search_endpoint: str
    azure_search_admin_key: str
    azure_search_index_name: str

    # chunking params - these seem to work well
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # how many docs to retrieve
    top_k_results: int = 3

    # temp for the llm - keeping it at 0 for consistent answers
    chat_temperature: float = 0.0

    class Config:
        env_file = ".env"

# singleton pattern
_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
