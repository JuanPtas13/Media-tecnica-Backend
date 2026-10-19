from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.repositories.config_horario_repository import ConfigHorarioRepository
from app.schemas.config_horario import ConfigHorarioCreate, ConfigHorarioUpdate, ConfigHorarioResponse


class ConfigHorarioService:
    """Servicio de lógica de negocio para ConfigHorario"""
    
    def __init__(self, db: Session):
        self.repository = ConfigHorarioRepository(db)

    @staticmethod
    def _minutos_entre(inicio, limite) -> int:
        inicio_minutos = inicio.hour * 60 + inicio.minute
        limite_minutos = limite.hour * 60 + limite.minute
        return limite_minutos - inicio_minutos

    @staticmethod
    def _validar_horario(inicio, limite, cierre, aplica_desde, aplica_hasta):
        if inicio > limite:
            raise ValueError("La hora límite debe ser igual o posterior al inicio de clase")
        if limite > cierre:
            raise ValueError("El cierre debe ser igual o posterior a la hora límite")
        if aplica_hasta and aplica_desde > aplica_hasta:
            raise ValueError("La fecha final debe ser igual o posterior a la fecha inicial")
    
    def crear_config(self, config_in: ConfigHorarioCreate) -> ConfigHorarioResponse:
        """Crear nueva configuración horaria"""
        datos = config_in.model_dump()
        datos["min_tolerancia"] = self._minutos_entre(
            config_in.hora_inicio_clase,
            config_in.hora_limite_ingreso,
        )
        config = self.repository.create(datos)
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
        actual = self.repository.get_by_id(config_id)
        if not actual:
            return None

        datos_actualizacion = config_in.model_dump(exclude_unset=True)
        inicio = datos_actualizacion.get("hora_inicio_clase", actual.hora_inicio_clase)
        limite = datos_actualizacion.get("hora_limite_ingreso", actual.hora_limite_ingreso)
        cierre = datos_actualizacion.get("hora_cierre_asistencia", actual.hora_cierre_asistencia)
        aplica_desde = datos_actualizacion.get("aplica_desde", actual.aplica_desde)
        aplica_hasta = datos_actualizacion.get("aplica_hasta", actual.aplica_hasta)
        if not all((inicio, limite, cierre, aplica_desde)):
            raise ValueError("Las horas y la fecha inicial son obligatorias")
        self._validar_horario(inicio, limite, cierre, aplica_desde, aplica_hasta)
        datos_actualizacion["min_tolerancia"] = self._minutos_entre(inicio, limite)

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
