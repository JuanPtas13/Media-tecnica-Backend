from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class RolBase(BaseModel):
    """Base para Rol"""
    nombre: str = Field(..., min_length=1, max_length=100)
    permisos: Optional[str] = None
    descripcion: Optional[str] = None


class RolCreate(RolBase):
    """Schema para crear Rol"""
    pass


class RolUpdate(BaseModel):
    """Schema para actualizar Rol"""
    nombre: Optional[str] = None
    permisos: Optional[str] = None
    descripcion: Optional[str] = None


class RolResponse(RolBase):
    """Schema de respuesta para Rol"""
    id_roles: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
