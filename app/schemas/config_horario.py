from typing import Optional
from datetime import datetime, time, date
from pydantic import BaseModel, Field


class ConfigHorarioBase(BaseModel):
    """Base para ConfigHorario"""
    hora_inicio_clase: time
    hora_limite_ingreso: time
    min_tolerancia: int = Field(..., ge=0)
    aplica_desde: date
    aplica_hasta: date
    estado: bool = True


class ConfigHorarioCreate(ConfigHorarioBase):
    """Schema para crear ConfigHorario"""
    pass


class ConfigHorarioUpdate(BaseModel):
    """Schema para actualizar ConfigHorario"""
    hora_inicio_clase: Optional[time] = None
    hora_limite_ingreso: Optional[time] = None
    min_tolerancia: Optional[int] = None
    aplica_desde: Optional[date] = None
    aplica_hasta: Optional[date] = None
    estado: Optional[bool] = None


class ConfigHorarioResponse(ConfigHorarioBase):
    """Schema de respuesta para ConfigHorario"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
