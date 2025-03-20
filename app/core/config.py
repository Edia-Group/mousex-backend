from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    """
    Classe di configurazione per l'applicazione.
    """
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    SECRET_KEY: str = "inserire_chiave_segreta_sicura"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 400
    OTP_EXPIRATION_SECONDS: int = 300

    class Config:
        env_file = ".env"


settings = Settings()