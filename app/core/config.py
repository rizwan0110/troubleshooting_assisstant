from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool
    VERSION: str
    GROQ_API_KEY: str
    MODEL_NAME: str
    HYBRID_ALPHA: float  # weight between dense and sparse retrieval (0=BM25, 1=dense)
    RERANKER_MODEL: str
    EMBEDDING_MODEL: str


    class Config:
        env_file = ".env"


settings = Settings()
