from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GradoBase(BaseModel):
    """Base para Grado"""
    numero_grado: int = Field(..., ge=1, le=12)
    grupo: str = Field(..., min_length=1, max_length=50)
    estado: bool = True


class GradoCreate(GradoBase):
    """Schema para crear Grado"""
    pass


class GradoUpdate(BaseModel):
    """Schema para actualizar Grado"""
    numero_grado: Optional[int] = None
    grupo: Optional[str] = None
    estado: Optional[bool] = None


class GradoResponse(GradoBase):
    """Schema de respuesta para Grado"""
    id_grado: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

