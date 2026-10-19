from typing import List
from sqlalchemy.orm import Session
from app.repositories.permiso_repository import PermisoRepository
from app.repositories.rol_permiso_repository import RolPermisoRepository


class PermisoService:
    """Servicio de lógica de negocio para Permisos"""
    
    def __init__(self, db: Session):
        self.permiso_repo = PermisoRepository(db)
        self.rol_permiso_repo = RolPermisoRepository(db)
    
    def obtener_permisos_usuario(self, usuario_id: int) -> List[str]:
        """
        Obtener los permisos de un usuario.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Lista de nombres de permisos
        """
        return self.permiso_repo.obtener_permisos_por_usuario(usuario_id)
    
    def obtener_permisos_rol(self, rol_id: int) -> List[str]:
        """
        Obtener los permisos de un rol.
        
        Args:
            rol_id: ID del rol
            
        Returns:
            Lista de nombres de permisos
        """
        return self.permiso_repo.obtener_permisos_por_rol(rol_id)
    
    def usuario_tiene_permiso(self, usuario_id: int, permiso: str) -> bool:
        """
        Verificar si un usuario tiene un permiso específico.
        
        Args:
            usuario_id: ID del usuario
            permiso: Nombre del permiso
            
        Returns:
            True si el usuario tiene el permiso, False en caso contrario
        """
        permisos = self.obtener_permisos_usuario(usuario_id)
        return permiso in permisos
    
    def usuario_tiene_alguno_de(self, usuario_id: int, permisos: List[str]) -> bool:
        """
        Verificar si un usuario tiene al menos uno de los permisos especificados.
        
        Args:
            usuario_id: ID del usuario
            permisos: Lista de permisos a verificar
            
        Returns:
            True si el usuario tiene al menos uno de los permisos
        """
        permisos_usuario = self.obtener_permisos_usuario(usuario_id)
        return any(p in permisos_usuario for p in permisos)
    
    def usuario_tiene_todos(self, usuario_id: int, permisos: List[str]) -> bool:
        """
        Verificar si un usuario tiene todos los permisos especificados.
        
        Args:
            usuario_id: ID del usuario
            permisos: Lista de permisos a verificar
            
        Returns:
            True si el usuario tiene todos los permisos
        """
        permisos_usuario = self.obtener_permisos_usuario(usuario_id)
        return all(p in permisos_usuario for p in permisos)
    
    def asignar_permiso_a_rol(self, rol_id: int, permiso_id: int):
        """
        Asignar un permiso a un rol.
        
        Args:
            rol_id: ID del rol
            permiso_id: ID del permiso
        """
        return self.rol_permiso_repo.asignar_permiso_a_rol(rol_id, permiso_id)
    
    def remover_permiso_de_rol(self, rol_id: int, permiso_id: int) -> bool:
        """
        Remover un permiso de un rol.
        
        Args:
            rol_id: ID del rol
            permiso_id: ID del permiso
            
        Returns:
            True si se removió, False si no existía
        """
        return self.rol_permiso_repo.remover_permiso_de_rol(rol_id, permiso_id)
