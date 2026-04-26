from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional


class LoginRequest(BaseModel):
    """Schema para Login"""
    email: EmailStr
    contraseña: str = Field(..., min_length=8, max_length=72)
    
    @field_validator('contraseña')
    @classmethod
    def validar_contrasena_bytes(cls, v):
        """Validar que la contraseña no exceda 72 bytes en UTF-8"""
        print(f"[VALIDATOR AUTH] Validando contraseña: {len(v)} chars, {len(v.encode('utf-8'))} bytes")
        bytes_length = len(v.encode('utf-8'))
        if bytes_length > 72:
            print(f"[VALIDATOR AUTH] Rechazando: {bytes_length} bytes > 72")
            raise ValueError(
                f"La contraseña no puede exceder 72 bytes en UTF-8 (recibido: {bytes_length} bytes)"
            )
        print(f"[VALIDATOR AUTH] Aceptando")
        return v


class TokenResponse(BaseModel):
    """Schema de respuesta de Token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Schema para refresh token"""
    refresh_token: str


class UsuarioAutenticado(BaseModel):
    """Schema del usuario autenticado con sus permisos"""
    id: int
    email: str
    nombre: str
    apellido1: Optional[str] = None
    apellido2: Optional[str] = None
    rol: Optional[str] = None
    rol_id: Optional[int] = None
    permisos: List[str] = []
    estado: bool = True
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Response completo del login con usuario y token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    usuario: UsuarioAutenticado
