from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.registro import RegistroIngreso
from app.models.estudiante import Estudiante


class ReporteRepository:
    """Repository para generar reportes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def asistencia_por_grado(self, grado_id: int, fecha: date) -> dict:
        """Obtener resumen de asistencia por grado en una fecha"""
        
        total_estudiantes = self.db.query(func.count(Estudiante.id_estudiante)).filter(
            Estudiante.grado_id == grado_id,
            Estudiante.estado == True
        ).scalar() or 0
        
        presentes = self.db.query(func.count(RegistroIngreso.id)).join(Estudiante).filter(
            Estudiante.grado_id == grado_id,
            RegistroIngreso.fecha == fecha,
            RegistroIngreso.estado == "entrada"
        ).scalar() or 0
        
        return {
            "grado_id": grado_id,
            "fecha": fecha,
            "total_estudiantes": total_estudiantes,
            "presentes": presentes,
            "ausentes": total_estudiantes - presentes,
            "porcentaje_asistencia": (presentes / total_estudiantes * 100) if total_estudiantes > 0 else 0
        }
    
    def asistencia_por_estudiante(self, estudiante_id: int, fecha_inicio: date, fecha_fin: date) -> dict:
        """Obtener reporte de asistencia de un estudiante en un rango de fechas"""
        
        registros = self.db.query(RegistroIngreso).filter(
            RegistroIngreso.estudiante_id == estudiante_id,
            RegistroIngreso.fecha >= fecha_inicio,
            RegistroIngreso.fecha <= fecha_fin
        ).all()

        entradas = len([r for r in registros if r.estado == "entrada"])
        
        return {
            "estudiante_id": estudiante_id,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "entradas": entradas,
            "total_registros": len(registros),
            "registros": registros
        }
    
    def actividad_por_rango(self, fecha_inicio: date, fecha_fin: date) -> dict:
        """Obtener actividad global en un rango de fechas"""
        
        entradas = self.db.query(func.count(RegistroIngreso.id)).filter(
            RegistroIngreso.fecha >= fecha_inicio,
            RegistroIngreso.fecha <= fecha_fin,
            RegistroIngreso.estado == "entrada"
        ).scalar() or 0
        
        return {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "total_entradas": entradas,
            "total_registros": entradas
        }

