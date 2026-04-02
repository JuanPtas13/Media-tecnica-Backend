from pydantic import BaseModel
from typing import Optional


class PermisoBase(BaseModel):
    """Schema base para Permiso"""
    nombre: str
    descripcion: Optional[str] = None


class PermisoCreate(PermisoBase):
    """Schema para crear un Permiso"""
    pass


class PermisoUpdate(BaseModel):
    """Schema para actualizar un Permiso"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class PermisoResponse(PermisoBase):
    """Schema de respuesta para Permiso"""
    id_permiso: int
    
    class Config:
        from_attributes = True
