from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Base de datos
    DATABASE_URL: str = "postgresql://postgres.lmxdctredhdwtmizhxor:ar$sf6#Fw8p?-hX@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
    
    # App
    APP_NAME: str = "Media Técnica Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # JWT
    JWT_SECRET_KEY: str = "tu-clave-secreta-muy-segura-cambiar-en-produccion"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Obtener configuración (cacheada)"""
    return Settings()
