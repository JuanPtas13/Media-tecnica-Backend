from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.repositories.base_repositorie import BaseRepository
from app.models.permiso import Permiso


class PermisoRepository(BaseRepository):
    """Repositorio para gestión de permisos"""
    
    def __init__(self, db: Session):
        super().__init__(Permiso, db)
    
    def obtener_permisos_por_usuario(self, usuario_id: int) -> List[str]:
        """
        Obtener los permisos de un usuario desde la BD.
        Ejecuta la query:
        SELECT p.nombre
        FROM usuarios u
        JOIN roles r ON u.rol_id = r.id_roles
        JOIN rol_permiso rp ON r.id_roles = rp.id_rol
        JOIN permisos p ON rp.id_permiso = p.id_permiso
        WHERE u.id_usuario = :user_id
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Lista de nombres de permisos
        """
        from app.models.usuario import Usuario
        from app.models.rol import Rol
        from app.models.rol_permiso import RolPermiso
        
        try:
            permisos = self.db.query(Permiso.nombre).join(
                RolPermiso, RolPermiso.id_permiso == Permiso.id_permiso
            ).join(
                Rol, Rol.id_roles == RolPermiso.id_rol
            ).join(
                Usuario, Usuario.rol_id == Rol.id_roles
            ).filter(
                Usuario.id_usuario == usuario_id
            ).all()
            
            return [permiso[0] for permiso in permisos]
        except Exception as e:
            raise Exception(f"Error al obtener permisos del usuario: {str(e)}")
    
    def obtener_permisos_por_rol(self, rol_id: int) -> List[str]:
        """
        Obtener los permisos de un rol.
        
        Args:
            rol_id: ID del rol
            
        Returns:
            Lista de nombres de permisos
        """
        from app.models.rol_permiso import RolPermiso
        
        try:
            permisos = self.db.query(Permiso.nombre).join(
                RolPermiso, RolPermiso.id_permiso == Permiso.id_permiso
            ).filter(
                RolPermiso.id_rol == rol_id
            ).all()
            
            return [permiso[0] for permiso in permisos]
        except Exception as e:
            raise Exception(f"Error al obtener permisos del rol: {str(e)}")
    
    def obtener_por_nombre(self, nombre: str) -> Permiso:
        """Obtener permiso por nombre"""
        try:
            return self.db.query(Permiso).filter(Permiso.nombre == nombre).first()
        except Exception as e:
            raise Exception(f"Error al obtener permiso: {str(e)}")
