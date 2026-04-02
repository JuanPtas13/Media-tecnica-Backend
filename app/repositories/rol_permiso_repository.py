from sqlalchemy.orm import Session
from app.repositories.base_repositorie import BaseRepository
from app.models.rol_permiso import RolPermiso


class RolPermisoRepository(BaseRepository):
    """Repositorio para gestión de relaciones rol-permiso"""
    
    def __init__(self, db: Session):
        super().__init__(RolPermiso, db)
    
    def asignar_permiso_a_rol(self, rol_id: int, permiso_id: int) -> RolPermiso:
        """
        Asignar un permiso a un rol.
        
        Args:
            rol_id: ID del rol
            permiso_id: ID del permiso
            
        Returns:
            Registro de RolPermiso creado
        """
        try:
            # Verificar si ya existe
            existente = self.db.query(RolPermiso).filter(
                RolPermiso.id_rol == rol_id,
                RolPermiso.id_permiso == permiso_id
            ).first()
            
            if existente:
                return existente
            
            # Crear nuevo
            rol_permiso = RolPermiso(id_rol=rol_id, id_permiso=permiso_id)
            self.db.add(rol_permiso)
            self.db.commit()
            self.db.refresh(rol_permiso)
            return rol_permiso
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error al asignar permiso a rol: {str(e)}")
    
    def remover_permiso_de_rol(self, rol_id: int, permiso_id: int) -> bool:
        """
        Remover un permiso de un rol.
        
        Args:
            rol_id: ID del rol
            permiso_id: ID del permiso
            
        Returns:
            True si se removió, False si no existía
        """
        try:
            resultado = self.db.query(RolPermiso).filter(
                RolPermiso.id_rol == rol_id,
                RolPermiso.id_permiso == permiso_id
            ).delete()
            
            self.db.commit()
            return resultado > 0
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error al remover permiso de rol: {str(e)}")
