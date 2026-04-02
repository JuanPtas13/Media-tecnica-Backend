from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class EstudianteBase(BaseModel):
    """Base para Estudiante"""
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido1: str = Field(..., min_length=1, max_length=100)
    apellido2: Optional[str] = Field(None, max_length=100)
    documento: str = Field(..., min_length=1, max_length=50)
    grado_id: Optional[int] = None
    codigo_qr: Optional[str] = None
    estado: bool = True


class EstudianteCreate(EstudianteBase):
    """Schema para crear Estudiante"""
    pass


class EstudianteUpdate(BaseModel):
    """Schema para actualizar Estudiante"""
    nombre: Optional[str] = None
    apellido1: Optional[str] = None
    apellido2: Optional[str] = None
    documento: Optional[str] = None
    grado_id: Optional[int] = None
    codigo_qr: Optional[str] = None
    estado: Optional[bool] = None


class EstudianteResponse(EstudianteBase):
    """Schema de respuesta para Estudiante"""
    id_estudiante: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

