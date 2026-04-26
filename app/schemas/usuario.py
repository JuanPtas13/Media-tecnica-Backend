from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator


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
    contrasena: str = Field(..., min_length=8, max_length=72)
    
    @field_validator('contrasena')
    @classmethod
    def validar_contrasena_bytes(cls, v):
        """Validar que la contraseña no exceda 72 bytes en UTF-8"""
        print(f"[VALIDATOR] Validando contraseña: {len(v)} chars, {len(v.encode('utf-8'))} bytes")
        bytes_length = len(v.encode('utf-8'))
        if bytes_length > 72:
            print(f"[VALIDATOR] Rechazando: {bytes_length} bytes > 72")
            raise ValueError(
                f"La contraseña no puede exceder 72 bytes en UTF-8 "
                f"(recibido: {bytes_length} bytes). "
                f"Usa contraseñas más simples o más cortas."
            )
        print(f"[VALIDATOR] Aceptando")
        return v

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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
