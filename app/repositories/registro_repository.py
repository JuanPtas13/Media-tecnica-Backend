from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from app.models.registro import RegistroIngreso
from app.repositories.base_repositorie import BaseRepository


class RegistroRepository(BaseRepository[RegistroIngreso]):
    """Repository específico para RegistroIngreso (asistencia)"""
    
    def __init__(self, db: Session):
        super().__init__(RegistroIngreso, db)
    
    def get_by_estudiante(self, estudiante_id: int, skip: int = 0, limit: int = 100) -> List[RegistroIngreso]:
        """Obtener registros de un estudiante"""
        return self.db.query(self.model).filter(
            self.model.estudiante_id == estudiante_id
        ).order_by(self.model.fecha.desc(), self.model.hora.desc()).offset(skip).limit(limit).all()
    
    def get_by_usuario(self, usuario_id: int, skip: int = 0, limit: int = 100) -> List[RegistroIngreso]:
        """Obtener registros de un usuario (quien registra)"""
        return self.db.query(self.model).filter(
            self.model.usuario_id == usuario_id
        ).offset(skip).limit(limit).all()
    
    def get_por_fecha(self, fecha: date, skip: int = 0, limit: int = 100) -> List[RegistroIngreso]:
        """Obtener registros de una fecha específica"""
        return self.db.query(self.model).filter(
            self.model.fecha == fecha
        ).offset(skip).limit(limit).all()
    
    def get_por_estado(self, estado: str, skip: int = 0, limit: int = 100) -> List[RegistroIngreso]:
        """Obtener registros por estado (entrada, salida, etc)"""
        return self.db.query(self.model).filter(
            self.model.estado == estado
        ).offset(skip).limit(limit).all()
    
    def get_ultimos_registros(self, limite: int = 50) -> List[RegistroIngreso]:
        """Obtener los últimos registros"""
        return self.db.query(self.model).order_by(
            self.model.fecha.desc(), self.model.hora.desc()
        ).limit(limite).all()
    
    def get_por_config(self, config_id: int, skip: int = 0, limit: int = 100) -> List[RegistroIngreso]:
        """Obtener registros de una configuración horaria"""
        return self.db.query(self.model).filter(
            self.model.config_id == config_id
        ).offset(skip).limit(limit).all()
