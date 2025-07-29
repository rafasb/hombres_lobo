# Configuración general del proyecto
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Hombres Lobo"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./hombreslobo.db")

settings = Settings()
