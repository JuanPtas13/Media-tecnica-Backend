from app.repositories.base_repositorie import BaseRepository
from app.repositories.estudiante_repository import EstudianteRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.registro_repository import RegistroRepository
from app.repositories.grado_repository import GradoRepository
from app.repositories.rol_repository import RolRepository
from app.repositories.config_horario_repository import ConfigHorarioRepository
from app.repositories.permiso_repository import PermisoRepository
from app.repositories.rol_permiso_repository import RolPermisoRepository

__all__ = [
    "BaseRepository",
    "EstudianteRepository",
    "UsuarioRepository",
    "RegistroRepository",
    "GradoRepository",
    "RolRepository",
    "ConfigHorarioRepository",
    "PermisoRepository",
    "RolPermisoRepository"
]
