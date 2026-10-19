from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.repositories.registro_repository import RegistroRepository
from app.schemas.registro import RegistroIngresoCreate, RegistroIngresoUpdate, RegistroIngresoResponse


class RegistroService:
    """Servicio de lógica de negocio para RegistroIngreso"""
    
    def __init__(self, db: Session):
        self.repository = RegistroRepository(db)
    
    def crear_registro(self, registro_in: RegistroIngresoCreate) -> RegistroIngresoResponse:
        """Crear nuevo registro"""
        registro = self.repository.create(registro_in.dict())
        return RegistroIngresoResponse.from_orm(registro)
    
    def obtener_registro(self, registro_id: int) -> Optional[RegistroIngresoResponse]:
        """Obtener registro por ID"""
        registro = self.repository.get_by_id(registro_id)
        if not registro:
            return None
        return RegistroIngresoResponse.from_orm(registro)
    
    def obtener_todos(self, skip: int = 0, limit: int = 100) -> List[RegistroIngresoResponse]:
        """Obtener todos los registros"""
        registros = self.repository.get_all(skip, limit)
        return [RegistroIngresoResponse.from_orm(reg) for reg in registros]
    
    def actualizar_registro(self, registro_id: int, registro_in: RegistroIngresoUpdate) -> Optional[RegistroIngresoResponse]:
        """Actualizar registro"""
        datos_actualizacion = {k: v for k, v in registro_in.dict().items() if v is not None}
        
        registro = self.repository.update(registro_id, datos_actualizacion)
        if not registro:
            return None
        
        return RegistroIngresoResponse.from_orm(registro)
    
    def eliminar_registro(self, registro_id: int) -> bool:
        """Eliminar registro"""
        return self.repository.delete(registro_id)
    
    def obtener_por_estudiante(self, estudiante_id: int, skip: int = 0, limit: int = 100) -> List[RegistroIngresoResponse]:
        """Obtener registros de un estudiante"""
        registros = self.repository.get_by_estudiante(estudiante_id, skip, limit)
        return [RegistroIngresoResponse.from_orm(reg) for reg in registros]
    
    def obtener_por_usuario(self, usuario_id: int, skip: int = 0, limit: int = 100) -> List[RegistroIngresoResponse]:
        """Obtener registros de un usuario"""
        registros = self.repository.get_by_usuario(usuario_id, skip, limit)
        return [RegistroIngresoResponse.from_orm(reg) for reg in registros]
    
    def obtener_por_fecha(self, fecha: date, skip: int = 0, limit: int = 100) -> List[RegistroIngresoResponse]:
        """Obtener registros por fecha"""
        registros = self.repository.get_por_fecha(fecha, skip, limit)
        return [RegistroIngresoResponse.from_orm(reg) for reg in registros]
    
    def obtener_por_estado(self, estado: str, skip: int = 0, limit: int = 100) -> List[RegistroIngresoResponse]:
        """Obtener registros por estado"""
        registros = self.repository.get_por_estado(estado, skip, limit)
        return [RegistroIngresoResponse.from_orm(reg) for reg in registros]
    
    def obtener_ultimos(self, cantidad: int = 10) -> List[RegistroIngresoResponse]:
        """Obtener últimos registros."""
        registros = self.repository.get_ultimos_registros(cantidad)
        return [RegistroIngresoResponse.from_orm(reg) for reg in registros]

