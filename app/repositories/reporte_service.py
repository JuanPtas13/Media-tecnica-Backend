"""Consultas de asistencia y actividad que alimentan los reportes del sistema."""

from datetime import datetime, date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.models.config_horario import ConfigHorario
from app.models.registro import RegistroIngreso
from app.models.estudiante import Estudiante


def _minutos_retraso(registro: RegistroIngreso) -> Optional[int]:
    """Devuelve el retraso guardado o lo calcula desde la hora de inicio configurada."""
    minutos_guardados = registro.min_retraso
    if minutos_guardados is not None and not (
        registro.estado == "tarde" and minutos_guardados == 0
    ):
        return minutos_guardados

    if registro.hora is None or registro.config is None:
        return minutos_guardados

    hora_ingreso = registro.hora.hour * 60 + registro.hora.minute
    hora_inicio = (
        registro.config.hora_inicio_clase.hour * 60
        + registro.config.hora_inicio_clase.minute
    )
    return max(0, hora_ingreso - hora_inicio)


class ReporteRepository:
    """Consulta y prepara agregados de asistencia para las pantallas de reportes."""
    
    def __init__(self, db: Session):
        """Guarda la sesión que se utilizará en las consultas del repositorio."""
        self.db = db
    
    def asistencia_por_grado(self, grado_id: int, fecha: date) -> dict:
        """Resume presentes, ausentes y porcentaje para un grado en una fecha."""
        
        total_estudiantes = self.db.query(func.count(Estudiante.id_estudiante)).filter(
            Estudiante.grado_id == grado_id,
            Estudiante.estado == True
        ).scalar() or 0
        
        presentes = self.db.query(func.count(distinct(RegistroIngreso.estudiante_id))).join(Estudiante).filter(
            Estudiante.grado_id == grado_id,
            RegistroIngreso.fecha == fecha,
            RegistroIngreso.estado.in_(["a tiempo", "tarde"])
        ).scalar() or 0

        configuracion = self.db.query(ConfigHorario).filter(
            ConfigHorario.aplica_desde <= fecha,
            (ConfigHorario.aplica_hasta.is_(None)) | (ConfigHorario.aplica_hasta >= fecha),
            ConfigHorario.estado == True,
        ).first()
        ahora = datetime.now()
        asistencia_cerrada = bool(
            configuracion
            and fecha <= ahora.date()
            and (fecha < ahora.date() or ahora.time() >= configuracion.hora_cierre_asistencia)
        )
        ausentes = max(total_estudiantes - presentes, 0) if asistencia_cerrada else 0
        
        return {
            "grado_id": grado_id,
            "fecha": fecha,
            "total_estudiantes": total_estudiantes,
            "presentes": presentes,
            "ausentes": ausentes,
            "asistencia_cerrada": asistencia_cerrada,
            "hora_cierre_asistencia": configuracion.hora_cierre_asistencia if configuracion else None,
            "porcentaje_asistencia": (presentes / total_estudiantes * 100) if total_estudiantes > 0 else 0
        }
    
    def asistencia_por_estudiante(self, estudiante_id: int, fecha_inicio: date, fecha_fin: date) -> dict:
        """Lista registros del estudiante y calcula sus entradas en el rango solicitado."""
        registros = self.db.query(RegistroIngreso).filter(
            RegistroIngreso.estudiante_id == estudiante_id,
            RegistroIngreso.fecha >= fecha_inicio,
            RegistroIngreso.fecha <= fecha_fin
        ).all()

        entradas = len([r for r in registros if r.estado in ["a tiempo", "tarde"]])

        return {
            "estudiante_id": estudiante_id,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "entradas": entradas,
            "total_registros": len(registros),
            # Serializa manualmente las columnas necesarias para el reporte.
            "registros": [
                {
                    "id": r.id,
                    "fecha": str(r.fecha),
                    "hora": str(r.hora),
                    "estado": r.estado,
                    "estudiante_id": r.estudiante_id,
                    "usuario_id": r.usuario_id,
                    "min_retraso": _minutos_retraso(r),
                }
                for r in registros
            ]
        }
    
    def actividad_por_rango(self, fecha_inicio: date, fecha_fin: date) -> dict:
        """Devuelve el total y el detalle de entradas dentro del rango de fechas."""
        
        entradas = self.db.query(func.count(RegistroIngreso.id)).filter(
            RegistroIngreso.fecha >= fecha_inicio,
            RegistroIngreso.fecha <= fecha_fin,
            RegistroIngreso.estado.in_(["a tiempo", "tarde"])
        ).scalar() or 0
        registros = self.db.query(RegistroIngreso, Estudiante).join(
            Estudiante, RegistroIngreso.estudiante_id == Estudiante.id_estudiante
        ).filter(
            RegistroIngreso.fecha >= fecha_inicio,
            RegistroIngreso.fecha <= fecha_fin,
            RegistroIngreso.estado.in_(["a tiempo", "tarde"])
        ).order_by(RegistroIngreso.fecha.desc(), RegistroIngreso.hora.desc()).all()
        
        return {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "total_entradas": entradas,
            "total_registros": entradas,
            "registros": [
                {
                    "id": registro.id,
                    "fecha": str(registro.fecha),
                    "hora": str(registro.hora),
                    "estado": registro.estado,
                    "estudiante_id": registro.estudiante_id,
                    "estudiante": f"{estudiante.nombre} {estudiante.apellido1} {estudiante.apellido2 or ''}".strip(),
                    "documento": estudiante.documento,
                    "min_retraso": _minutos_retraso(registro),
                }
                for registro, estudiante in registros
            ],
        }
