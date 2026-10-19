from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.grado_repository import GradoRepository
from app.schemas.grado import GradoCreate, GradoUpdate, GradoResponse


class GradoService:
    """Servicio de lógica de negocio para Grado"""
    
    def __init__(self, db: Session):
        self.repository = GradoRepository(db)
    
    def crear_grado(self, grado_in: GradoCreate) -> GradoResponse:
        """Crear nuevo grado"""
        grado = self.repository.create(grado_in.dict())
        return GradoResponse.from_orm(grado)
    
    def obtener_grado(self, grado_id: int) -> Optional[GradoResponse]:
        """Obtener grado por ID"""
        grado = self.repository.get_by_id(grado_id)
        if not grado:
            return None
        return GradoResponse.from_orm(grado)
    
    def obtener_todos(self, skip: int = 0, limit: int = 100) -> List[GradoResponse]:
        """Obtener todos los grados"""
        grados = self.repository.get_all(skip, limit)
        return [GradoResponse.from_orm(grado) for grado in grados]
    
    def actualizar_grado(self, grado_id: int, grado_in: GradoUpdate) -> Optional[GradoResponse]:
        """Actualizar grado"""
        datos_actualizacion = {k: v for k, v in grado_in.dict().items() if v is not None}
        grado = self.repository.update(grado_id, datos_actualizacion)
        if not grado:
            return None
        return GradoResponse.from_orm(grado)
    
    def eliminar_grado(self, grado_id: int) -> bool:
        """Eliminar grado"""
        return self.repository.delete(grado_id)
    
    def obtener_por_numero(self, numero_grado: int) -> List[GradoResponse]:
        """Obtener grados por número"""
        grados = self.repository.get_por_numero(numero_grado)
        return [GradoResponse.from_orm(grado) for grado in grados]
    
    def obtener_activos(self, skip: int = 0, limit: int = 100) -> List[GradoResponse]:
        """Obtener grados activos"""
        grados = self.repository.get_activos(skip, limit)
        return [GradoResponse.from_orm(grado) for grado in grados]
