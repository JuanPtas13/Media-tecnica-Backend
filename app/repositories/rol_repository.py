from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.rol import Rol
from app.repositories.base_repositorie import BaseRepository


class RolRepository(BaseRepository[Rol]):
    """Repository específico para Rol"""
    
    def __init__(self, db: Session):
        super().__init__(Rol, db)
    
    def get_by_nombre(self, nombre: str) -> Optional[Rol]:
        """Obtener rol por nombre"""
        return self.db.query(self.model).filter(
            self.model.nombre == nombre
        ).first()
    
    def search_by_nombre(self, query: str, skip: int = 0, limit: int = 100) -> List[Rol]:
        """Buscar roles por nombre"""
        search_term = f"%{query}%"
        return self.db.query(self.model).filter(
            self.model.nombre.ilike(search_term)
        ).offset(skip).limit(limit).all()
