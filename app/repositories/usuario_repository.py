from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.repositories.base_repositorie import BaseRepository
#

class UsuarioRepository(BaseRepository[Usuario]):
    """Repository específico para Usuario"""
    
    def __init__(self, db: Session):
        super().__init__(Usuario, db)
    
    def get_by_correo(self, correo: str) -> Optional[Usuario]:
        """Obtener usuario por correo"""
        return self.db.query(self.model).filter(
            self.model.correo == correo
        ).first()
    
    def get_by_rol(self, rol_id: int, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Obtener usuarios por rol"""
        return self.db.query(self.model).filter(
            self.model.rol_id == rol_id
        ).offset(skip).limit(limit).all()
    
    def get_activos(self, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Obtener usuarios activos (estado=True)"""
        return self.db.query(self.model).filter(
            self.model.estado == True
        ).offset(skip).limit(limit).all()
    
    def existe_correo(self, correo: str) -> bool:
        """Verificar si existe un usuario con ese correo"""
        return self.db.query(
            self.db.query(self.model).filter(
                self.model.correo == correo
            ).exists()
        ).scalar()

