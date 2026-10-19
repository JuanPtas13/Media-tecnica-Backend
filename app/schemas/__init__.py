from app.schemas.estudiante import (
    EstudianteCreate,
    EstudianteUpdate,
    EstudianteResponse,
)
from app.schemas.grado import GradoCreate, GradoUpdate, GradoResponse
from app.schemas.registro import RegistroIngresoCreate, RegistroIngresoUpdate, RegistroIngresoResponse
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.schemas.rol import RolCreate, RolUpdate, RolResponse
from app.schemas.config_horario import ConfigHorarioCreate, ConfigHorarioUpdate, ConfigHorarioResponse
from app.schemas.auth import (
    LoginRequest, 
    TokenResponse, 
    RefreshTokenRequest,
    UsuarioAutenticado,
    LoginResponse
)
from app.schemas.permiso import PermisoCreate, PermisoUpdate, PermisoResponse
from app.schemas.rol_permiso import RolPermisoCreate, RolPermisoResponse

__all__ = [
    "EstudianteCreate",
    "EstudianteUpdate",
    "EstudianteResponse",
    "GradoCreate",
    "GradoUpdate",
    "GradoResponse",
    "RegistroIngresoCreate",
    "RegistroIngresoUpdate",
    "RegistroIngresoResponse",
    "UsuarioCreate",
    "UsuarioUpdate",
    "UsuarioResponse",
    "RolCreate",
    "RolUpdate",
    "RolResponse",
    "ConfigHorarioCreate",
    "ConfigHorarioUpdate",
    "ConfigHorarioResponse",
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "UsuarioAutenticado",
    "LoginResponse",
    "PermisoCreate",
    "PermisoUpdate",
    "PermisoResponse",
    "RolPermisoCreate",
    "RolPermisoResponse",
]

