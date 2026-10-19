from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.rol_repository import RolRepository
from app.schemas.rol import RolCreate, RolUpdate, RolResponse


class RolService:
    """Servicio de lógica de negocio para Rol"""
    
    def __init__(self, db: Session):
        self.repository = RolRepository(db)
    
    def crear_rol(self, rol_in: RolCreate) -> RolResponse:
        """Crear nuevo rol"""
        rol = self.repository.create(rol_in.dict())
        return RolResponse.from_orm(rol)
    
    def obtener_rol(self, rol_id: int) -> Optional[RolResponse]:
        """Obtener rol por ID"""
        rol = self.repository.get_by_id(rol_id)
        if not rol:
            return None
        return RolResponse.from_orm(rol)
    
    def obtener_todos(self, skip: int = 0, limit: int = 100) -> List[RolResponse]:
        """Obtener todos los roles"""
        roles = self.repository.get_all(skip, limit)
        return [RolResponse.from_orm(rol) for rol in roles]
    
    def actualizar_rol(self, rol_id: int, rol_in: RolUpdate) -> Optional[RolResponse]:
        """Actualizar rol"""
        datos_actualizacion = {k: v for k, v in rol_in.dict().items() if v is not None}
        rol = self.repository.update(rol_id, datos_actualizacion)
        if not rol:
            return None
        return RolResponse.from_orm(rol)
    
    def eliminar_rol(self, rol_id: int) -> bool:
        """Eliminar rol"""
        return self.repository.delete(rol_id)
    
    def obtener_por_nombre(self, nombre: str) -> Optional[RolResponse]:
        """Obtener rol por nombre"""
        rol = self.repository.get_by_nombre(nombre)
        if not rol:
            return None
        return RolResponse.from_orm(rol)
    
    def buscar(self, query: str, skip: int = 0, limit: int = 100) -> List[RolResponse]:
        """Buscar roles por nombre"""
        roles = self.repository.search_by_nombre(query, skip, limit)
        return [RolResponse.from_orm(rol) for rol in roles]
