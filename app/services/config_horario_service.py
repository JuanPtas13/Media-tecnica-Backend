from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.repositories.config_horario_repository import ConfigHorarioRepository
from app.schemas.config_horario import ConfigHorarioCreate, ConfigHorarioUpdate, ConfigHorarioResponse


class ConfigHorarioService:
    """Servicio de lógica de negocio para ConfigHorario"""
    
    def __init__(self, db: Session):
        self.repository = ConfigHorarioRepository(db)
    
    def crear_config(self, config_in: ConfigHorarioCreate) -> ConfigHorarioResponse:
        """Crear nueva configuración horaria"""
        config = self.repository.create(config_in.dict())
        return ConfigHorarioResponse.from_orm(config)
    
    def obtener_config(self, config_id: int) -> Optional[ConfigHorarioResponse]:
        """Obtener configuración por ID"""
        config = self.repository.get_by_id(config_id)
        if not config:
            return None
        return ConfigHorarioResponse.from_orm(config)
    
    def obtener_todos(self, skip: int = 0, limit: int = 100) -> List[ConfigHorarioResponse]:
        """Obtener todas las configuraciones"""
        configs = self.repository.get_all(skip, limit)
        return [ConfigHorarioResponse.from_orm(config) for config in configs]
    
    def actualizar_config(self, config_id: int, config_in: ConfigHorarioUpdate) -> Optional[ConfigHorarioResponse]:
        """Actualizar configuración"""
        datos_actualizacion = {k: v for k, v in config_in.dict().items() if v is not None}
        config = self.repository.update(config_id, datos_actualizacion)
        if not config:
            return None
        return ConfigHorarioResponse.from_orm(config)
    
    def eliminar_config(self, config_id: int) -> bool:
        """Eliminar configuración"""
        return self.repository.delete(config_id)
    
    def obtener_activos(self, skip: int = 0, limit: int = 100) -> List[ConfigHorarioResponse]:
        """Obtener configuraciones activas"""
        configs = self.repository.get_activos(skip, limit)
        return [ConfigHorarioResponse.from_orm(config) for config in configs]
    
    def obtener_vigente(self) -> Optional[ConfigHorarioResponse]:
        """Obtener configuración vigente (activa en fecha actual)"""
        config = self.repository.get_vigente()
        if not config:
            return None
        return ConfigHorarioResponse.from_orm(config)
    
    def obtener_en_fecha(self, fecha: date) -> Optional[ConfigHorarioResponse]:
        """Obtener configuración en fecha específica"""
        config = self.repository.get_en_fecha(fecha)
        if not config:
            return None
        return ConfigHorarioResponse.from_orm(config)
