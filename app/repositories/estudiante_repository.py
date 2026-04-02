from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.estudiante import Estudiante
from app.repositories.base_repositorie import BaseRepository


class EstudianteRepository(BaseRepository[Estudiante]):
    """Repository específico para Estudiante"""
    
    def __init__(self, db: Session):
        super().__init__(Estudiante, db)
    
    def get_by_documento(self, documento: str) -> Optional[Estudiante]:
        """Obtener estudiante por documento"""
        return self.db.query(self.model).filter(
            self.model.documento == documento
        ).first()
    
    def get_by_codigo_qr(self, codigo_qr: str) -> Optional[Estudiante]:
        """Obtener estudiante por código QR"""
        return self.db.query(self.model).filter(
            self.model.codigo_qr == codigo_qr
        ).first()
    
    def get_by_grado(self, grado_id: int, skip: int = 0, limit: int = 100) -> List[Estudiante]:
        """Obtener estudiantes por grado"""
        return self.db.query(self.model).filter(
            self.model.grado_id == grado_id
        ).offset(skip).limit(limit).all()
    
    def get_activos(self, skip: int = 0, limit: int = 100) -> List[Estudiante]:
        """Obtener estudiantes activos (estado=True)"""
        return self.db.query(self.model).filter(
            self.model.estado == True
        ).offset(skip).limit(limit).all()
    
    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Estudiante]:
        """Buscar estudiantes por nombre o documento"""
        search_term = f"%{query}%"
        return self.db.query(self.model).filter(
            (self.model.nombre.ilike(search_term)) |
            (self.model.apellido1.ilike(search_term)) |
            (self.model.documento.ilike(search_term))
        ).offset(skip).limit(limit).all()

