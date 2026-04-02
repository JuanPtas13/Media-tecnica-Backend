from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UsuarioBase(BaseModel):
    """Base para Usuario"""
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido1: str = Field(..., min_length=1, max_length=100)
    apellido2: Optional[str] = Field(None, max_length=100)
    correo: EmailStr
    rol_id: Optional[int] = None
    estado: bool = True


class UsuarioCreate(UsuarioBase):
    """Schema para crear Usuario"""
    contrasena: str = Field(..., min_length=8, max_length=255)

class UsuarioUpdate(BaseModel):
    """Schema para actualizar Usuario"""
    nombre: Optional[str] = None
    apellido1: Optional[str] = None
    apellido2: Optional[str] = None
    correo: Optional[EmailStr] = None
    rol_id: Optional[int] = None
    estado: Optional[bool] = None


class UsuarioResponse(BaseModel):
    """Schema de respuesta para Usuario (sin contraseña)"""
    id_usuario: int
    nombre: str
    apellido1: str
    apellido2: Optional[str]
    correo: str
    rol_id: Optional[int]
    estado: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
