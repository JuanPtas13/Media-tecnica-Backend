from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.grado import Grado
from app.repositories.base_repositorie import BaseRepository


class GradoRepository(BaseRepository[Grado]):
    """Repository específico para Grado"""
    
    def __init__(self, db: Session):
        super().__init__(Grado, db)
    
    def get_by_numero(self, numero: int) -> Optional[Grado]:
        """Obtener grado por número"""
        return self.db.query(self.model).filter(
            self.model.numero_grado == numero
        ).first()
    
    def get_by_numero_grupo(self, numero: int, grupo: str) -> Optional[Grado]:
        """Obtener grado específico por número y grupo"""
        return self.db.query(self.model).filter(
            (self.model.numero_grado == numero) &
            (self.model.grupo == grupo)
        ).first()
    
    def get_activos(self, skip: int = 0, limit: int = 100) -> List[Grado]:
        """Obtener grados activos (estado=True)"""
        return self.db.query(self.model).filter(
            self.model.estado == True
        ).offset(skip).limit(limit).all()
    
    def get_por_numero(self, numero: int, skip: int = 0, limit: int = 100) -> List[Grado]:
        """Obtener todos los grados de un número específico (con diferentes grupos)"""
        return self.db.query(self.model).filter(
            self.model.numero_grado == numero
        ).offset(skip).limit(limit).all()
