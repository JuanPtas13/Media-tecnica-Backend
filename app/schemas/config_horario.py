"""Esquemas Pydantic para validar y serializar configuraciones horarias."""

from typing import Optional
from datetime import datetime, time, date
from pydantic import BaseModel, Field, model_validator


class ConfigHorarioBase(BaseModel):
    """Base para ConfigHorario"""
    hora_inicio_clase: time
    hora_limite_ingreso: time
    hora_cierre_asistencia: time
    aplica_desde: date
    aplica_hasta: Optional[date] = None
    estado: bool = True


class ConfigHorarioCreate(ConfigHorarioBase):
    """Schema para crear ConfigHorario"""

    @model_validator(mode="after")
    def validar_horas(self):
        """Comprueba que los límites horarios y el rango de vigencia sean coherentes."""
        if self.hora_inicio_clase > self.hora_limite_ingreso:
            raise ValueError("La hora límite debe ser igual o posterior al inicio de clase")
        if self.hora_limite_ingreso > self.hora_cierre_asistencia:
            raise ValueError("El cierre debe ser igual o posterior a la hora límite")
        if self.aplica_hasta and self.aplica_desde > self.aplica_hasta:
            raise ValueError("La fecha final debe ser igual o posterior a la fecha inicial")
        return self


class ConfigHorarioUpdate(BaseModel):
    """Schema para actualizar ConfigHorario"""
    hora_inicio_clase: Optional[time] = None
    hora_limite_ingreso: Optional[time] = None
    hora_cierre_asistencia: Optional[time] = None
    aplica_desde: Optional[date] = None
    aplica_hasta: Optional[date] = None
    estado: Optional[bool] = None


class ConfigHorarioResponse(ConfigHorarioBase):
    """Schema de respuesta para ConfigHorario"""
    min_tolerancia: int = Field(ge=0)
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
