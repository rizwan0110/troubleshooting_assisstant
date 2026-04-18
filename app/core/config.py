from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool
    VERSION:float
    GROQ_API_KEY:str
    MODEL_NAME:str

    class Config:
        env_file = ".env"


settings = Settings()