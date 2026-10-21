"""Reglas de negocio para registrar y consultar entradas de estudiantes."""

from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.repositories.config_horario_repository import ConfigHorarioRepository
from app.repositories.registro_repository import RegistroRepository
from app.schemas.registro import RegistroIngresoCreate, RegistroIngresoUpdate, RegistroIngresoResponse


class RegistroService:
    """Coordina validaciones de asistencia y operaciones del repositorio."""
    
    def __init__(self, db: Session):
        """Inicializa el repositorio con la sesión de base de datos de la solicitud."""
        self.repository = RegistroRepository(db)
    
    def crear_registro(self, registro_in: RegistroIngresoCreate) -> RegistroIngresoResponse:
        """Valida vigencia y cierre de asistencia antes de guardar la entrada."""
        ahora = datetime.now()
        config = ConfigHorarioRepository(self.repository.db).get_en_fecha(ahora.date())
        if not config:
            raise ValueError("No hay una configuración horaria vigente para hoy.")
        if registro_in.config_id != config.id:
            raise ValueError("La configuración horaria del registro ya no está vigente.")
        if ahora.time() >= config.hora_cierre_asistencia:
            raise ValueError(
                f"La asistencia está cerrada desde las {config.hora_cierre_asistencia.strftime('%H:%M')}."
            )

        registro = self.repository.create(registro_in.dict())
        return RegistroIngresoResponse.from_orm(registro)
    
    def obtener_registro(self, registro_id: int) -> Optional[RegistroIngresoResponse]:
        """Busca una entrada por identificador y devuelve None si no existe."""
        registro = self.repository.get_by_id(registro_id)
        if not registro:
            return None
        return RegistroIngresoResponse.from_orm(registro)
    
    def obtener_todos(self, skip: int = 0, limit: int = 100) -> List[RegistroIngresoResponse]:
        """Lista entradas paginadas y las convierte al esquema de respuesta."""
        registros = self.repository.get_all(skip, limit)
        return [RegistroIngresoResponse.from_orm(reg) for reg in registros]
    
    def actualizar_registro(self, registro_id: int, registro_in: RegistroIngresoUpdate) -> Optional[RegistroIngresoResponse]:
        """Aplica únicamente los campos enviados y devuelve el registro actualizado."""
        datos_actualizacion = {k: v for k, v in registro_in.dict().items() if v is not None}
        
        registro = self.repository.update(registro_id, datos_actualizacion)
        if not registro:
            return None
        
        return RegistroIngresoResponse.from_orm(registro)
    
    def eliminar_registro(self, registro_id: int) -> bool:
        """Elimina una entrada y devuelve si el repositorio encontró el registro."""
        return self.repository.delete(registro_id)
    
    def obtener_por_estudiante(self, estudiante_id: int, skip: int = 0, limit: int = 100) -> List[RegistroIngresoResponse]:
        """Lista las entradas de un estudiante con paginación."""
        registros = self.repository.get_by_estudiante(estudiante_id, skip, limit)
        return [RegistroIngresoResponse.from_orm(reg) for reg in registros]
    
    def obtener_por_usuario(self, usuario_id: int, skip: int = 0, limit: int = 100) -> List[RegistroIngresoResponse]:
        """Lista las entradas creadas por un usuario con paginación."""
        registros = self.repository.get_by_usuario(usuario_id, skip, limit)
        return [RegistroIngresoResponse.from_orm(reg) for reg in registros]
    
    def obtener_por_fecha(self, fecha: date, skip: int = 0, limit: int = 100) -> List[RegistroIngresoResponse]:
        """Lista las entradas registradas en la fecha indicada."""
        registros = self.repository.get_por_fecha(fecha, skip, limit)
        return [RegistroIngresoResponse.from_orm(reg) for reg in registros]
    
    def obtener_por_estado(self, estado: str, skip: int = 0, limit: int = 100) -> List[RegistroIngresoResponse]:
        """Lista las entradas que coinciden con el estado solicitado."""
        registros = self.repository.get_por_estado(estado, skip, limit)
        return [RegistroIngresoResponse.from_orm(reg) for reg in registros]
    
    def obtener_ultimos(self, cantidad: int = 10) -> List[RegistroIngresoResponse]:
        """Devuelve las entradas más recientes, limitadas a la cantidad solicitada."""
        registros = self.repository.get_ultimos_registros(cantidad)
        return [RegistroIngresoResponse.from_orm(reg) for reg in registros]
