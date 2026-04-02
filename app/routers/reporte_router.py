from datetime import date
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import get_current_user, require_docente_or_admin
from app.services.reporte_service import ReporteService
from app.utils.responses import success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/asistencia/grado/{grado_id}", response_model=dict)
def asistencia_por_grado(
    grado_id: int,
    fecha: date = Query(...),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener reporte de asistencia por grado en una fecha - DOCENTE o ADMIN"""
    try:
        logger.info(f"Reporte asistencia por grado {grado_id} en fecha {fecha} | Usuario: {current_user.get('email')} | Rol: {current_user.get('rol')}")
        service = ReporteService(db)
        reporte = service.asistencia_por_grado(grado_id, fecha)
        
        return success_response(
            data=reporte,
            message="Reporte de asistencia obtenido exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/asistencia/estudiante/{estudiante_id}", response_model=dict)
def asistencia_por_estudiante(
    estudiante_id: int,
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener reporte de asistencia de un estudiante en un rango de fechas - DOCENTE o ADMIN"""
    try:
        logger.info(f"Reporte asistencia estudiante {estudiante_id} desde {fecha_inicio} hasta {fecha_fin} | Usuario: {current_user.get('email')} | Rol: {current_user.get('rol')}")
        if fecha_inicio > fecha_fin:
            raise HTTPException(status_code=400, detail="fecha_inicio no puede ser mayor que fecha_fin")
        
        service = ReporteService(db)
        reporte = service.asistencia_por_estudiante(estudiante_id, fecha_inicio, fecha_fin)
        
        return success_response(
            data=reporte,
            message="Reporte de asistencia obtenido exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actividad", response_model=dict)
def actividad_por_rango(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener reporte de actividad en un rango de fechas - DOCENTE o ADMIN"""
    try:
        logger.info(f"Reporte de actividad desde {fecha_inicio} hasta {fecha_fin} | Usuario: {current_user.get('email')} | Rol: {current_user.get('rol')}")
        if fecha_inicio > fecha_fin:
            raise HTTPException(status_code=400, detail="fecha_inicio no puede ser mayor que fecha_fin")
        
        service = ReporteService(db)
        reporte = service.actividad_por_rango(fecha_inicio, fecha_fin)
        
        return success_response(
            data=reporte,
            message="Reporte de actividad obtenido exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
