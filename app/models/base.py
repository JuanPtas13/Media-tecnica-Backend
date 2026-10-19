from app.core.database import Base


class BaseModel(Base):
    """Modelo base abstracto para todas las tablas"""
    
    __abstract__ = True
