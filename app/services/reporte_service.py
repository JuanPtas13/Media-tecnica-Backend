from datetime import date
from sqlalchemy.orm import Session
from app.repositories.reporte_service import ReporteRepository


class ReporteService:
    """Servicio de lógica de negocio para Reportes"""
    
    def __init__(self, db: Session):
        self.repository = ReporteRepository(db)
    
    def asistencia_por_grado(self, grado_id: int, fecha: date) -> dict:
        """Obtener reporte de asistencia por grado"""
        return self.repository.asistencia_por_grado(grado_id, fecha)
    
    def asistencia_por_estudiante(self, estudiante_id: int, fecha_inicio: date, fecha_fin: date) -> dict:
        """Obtener reporte de asistencia por estudiante"""
        return self.repository.asistencia_por_estudiante(estudiante_id, fecha_inicio, fecha_fin)
    
    def actividad_por_rango(self, fecha_inicio: date, fecha_fin: date) -> dict:
        """Obtener reporte de actividad en un rango de fechas"""
        return self.repository.actividad_por_rango(fecha_inicio, fecha_fin)
