from typing import Optional
from datetime import datetime, date, time
from pydantic import BaseModel, Field


class RegistroIngresoBase(BaseModel):
    """Base para RegistroIngreso"""
    estudiante_id: int
    usuario_id: int
    config_id: int
    fecha: date
    hora: time
    estado: str = Field(..., min_length=1, max_length=50)
    min_retraso: Optional[int] = None


class RegistroIngresoCreate(RegistroIngresoBase):
    """Schema para crear RegistroIngreso"""
    pass


class RegistroIngresoUpdate(BaseModel):
    """Schema para actualizar RegistroIngreso"""
    estudiante_id: Optional[int] = None
    usuario_id: Optional[int] = None
    config_id: Optional[int] = None
    fecha: Optional[date] = None
    hora: Optional[time] = None
    estado: Optional[str] = None
    min_retraso: Optional[int] = None


class RegistroIngresoResponse(RegistroIngresoBase):
    """Schema de respuesta para RegistroIngreso"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

