from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.estudiante_repository import EstudianteRepository
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate, EstudianteResponse


class EstudianteService:
    """Servicio de lógica de negocio para Estudiante"""
    
    def __init__(self, db: Session):
        self.repository = EstudianteRepository(db)
    
    def crear_estudiante(self, estudiante_in: EstudianteCreate) -> EstudianteResponse:
        """Crear nuevo estudiante"""
        # Validación de lógica de negocio
        if self.repository.get_by_documento(estudiante_in.documento):
            raise ValueError(f"Ya existe un estudiante con documento {estudiante_in.documento}")
        
        estudiante = self.repository.create(estudiante_in.dict())
        return EstudianteResponse.from_orm(estudiante)
    
    def obtener_estudiante(self, estudiante_id: int) -> Optional[EstudianteResponse]:
        """Obtener estudiante por ID"""
        estudiante = self.repository.get_by_id(estudiante_id)
        if not estudiante:
            return None
        return EstudianteResponse.from_orm(estudiante)
    
    def obtener_todos(self, skip: int = 0, limit: int = 100) -> List[EstudianteResponse]:
        """Obtener todos los estudiantes"""
        estudiantes = self.repository.get_all(skip, limit)
        return [EstudianteResponse.from_orm(est) for est in estudiantes]
    
    def actualizar_estudiante(self, estudiante_id: int, estudiante_in: EstudianteUpdate) -> Optional[EstudianteResponse]:
        """Actualizar estudiante"""
        # Validar que no exista otro con el mismo documento
        if estudiante_in.documento:
            existente = self.repository.get_by_documento(estudiante_in.documento)
            if existente and existente.id_estudiante != estudiante_id:
                raise ValueError(f"Ya existe otro estudiante con documento {estudiante_in.documento}")
        
        # Filtrar campos None
        datos_actualizacion = {k: v for k, v in estudiante_in.dict().items() if v is not None}
        
        estudiante = self.repository.update(estudiante_id, datos_actualizacion)
        if not estudiante:
            return None
        
        return EstudianteResponse.from_orm(estudiante)
    
    def eliminar_estudiante(self, estudiante_id: int) -> bool:
        """Eliminar estudiante"""
        return self.repository.delete(estudiante_id)
    
    def obtener_por_documento(self, documento: str) -> Optional[EstudianteResponse]:
        """Obtener estudiante por documento"""
        estudiante = self.repository.get_by_documento(documento)
        if not estudiante:
            return None
        return EstudianteResponse.from_orm(estudiante)
    
    def obtener_por_codigo_qr(self, codigo_qr: str) -> Optional[EstudianteResponse]:
        """Obtener estudiante por código QR"""
        estudiante = self.repository.get_by_codigo_qr(codigo_qr)
        if not estudiante:
            return None
        return EstudianteResponse.from_orm(estudiante)
    
    def obtener_por_grado(self, grado_id: int, skip: int = 0, limit: int = 100) -> List[EstudianteResponse]:
        """Obtener estudiantes por grado"""
        estudiantes = self.repository.get_by_grado(grado_id, skip, limit)
        return [EstudianteResponse.from_orm(est) for est in estudiantes]
    
    def obtener_activos(self, skip: int = 0, limit: int = 100) -> List[EstudianteResponse]:
        """Obtener estudiantes activos"""
        estudiantes = self.repository.get_activos(skip, limit)
        return [EstudianteResponse.from_orm(est) for est in estudiantes]
    
    def buscar(self, query: str, skip: int = 0, limit: int = 100) -> List[EstudianteResponse]:
        """Buscar estudiantes"""
        estudiantes = self.repository.search(query, skip, limit)
        return [EstudianteResponse.from_orm(est) for est in estudiantes]
    
    def total_estudiantes(self) -> int:
        """Obtener total de estudiantes"""
        return self.repository.count()
