from datetime import datetime
from sqlalchemy import Column, DateTime, func
from app.core.database import Base


class BaseModel(Base):
    """Modelo base con campos de auditoría comunes"""
    
    __abstract__ = True
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now(), nullable=False)
