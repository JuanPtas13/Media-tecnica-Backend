from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class LoginRequest(BaseModel):
    """Schema para Login"""
    email: EmailStr
    contraseña: str = Field(..., min_length=8)


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
