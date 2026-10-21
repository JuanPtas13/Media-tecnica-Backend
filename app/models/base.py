"""Base declarativa común para que SQLAlchemy registre todos los modelos."""

from app.core.database import Base


class BaseModel(Base):
    """Modelo base abstracto para todas las tablas"""
    
    __abstract__ = True
