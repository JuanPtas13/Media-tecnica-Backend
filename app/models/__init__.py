from app.models.base import BaseModel
from app.models.estudiante import Estudiante
from app.models.grado import Grado
from app.models.registro import RegistroIngreso
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.config_horario import ConfigHorario
from app.models.permiso import Permiso
from app.models.rol_permiso import RolPermiso

__all__ = [
    "BaseModel",
    "Estudiante",
    "Grado",
    "RegistroIngreso",
    "Usuario",
    "Rol",
    "ConfigHorario",
    "Permiso",
    "RolPermiso"
]
