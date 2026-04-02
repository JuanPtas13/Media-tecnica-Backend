from typing import List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import get_current_user, permiso_requerido, require_docente_or_admin, require_no_vigilante
from app.services.estudiante_service import EstudianteService
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate, EstudianteResponse
from app.utils.responses import success_response, error_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])


@router.get("/", response_model=dict)
def obtener_estudiantes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener lista de estudiantes - DOCENTE o ADMIN"""
    try:
        logger.info(f"Listado de estudiantes | Usuario: {current_user.get('email')} | Rol: {current_user.get('rol')}")
        service = EstudianteService(db)
        estudiantes = service.obtener_todos(skip, limit)
        total = service.total_estudiantes()
        
        return success_response(
            data={
                "estudiantes": estudiantes,
                "total": total,
                "skip": skip,
                "limit": limit
            },
            message="Estudiantes obtenidos exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/buscar", response_model=dict)
def buscar_estudiantes(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Buscar estudiantes por nombre o documento - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Buscar estudiantes: {query} | Usuario: {current_user.get('email')}")
        service = EstudianteService(db)
        estudiantes = service.buscar(query, skip, limit)
        
        return success_response(
            data=estudiantes,
            message=f"Se encontraron {len(estudiantes)} estudiantes"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activos", response_model=dict)
def obtener_estudiantes_activos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener lista de estudiantes activos - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Listado de estudiantes activos | Usuario: {current_user.get('email')}")
        service = EstudianteService(db)
        estudiantes = service.obtener_activos(skip, limit)
        
        return success_response(
            data=estudiantes,
            message="Estudiantes activos obtenidos exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grado/{grado_id}", response_model=dict)
def obtener_estudiantes_por_grado(
    grado_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener estudiantes de un grado específico - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Obtener estudiantes por grado {grado_id} | Usuario: {current_user.get('email')}")
        service = EstudianteService(db)
        estudiantes = service.obtener_por_grado(grado_id, skip, limit)
        
        return success_response(
            data=estudiantes,
            message=f"Se encontraron {len(estudiantes)} estudiantes en el grado"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{estudiante_id}", response_model=dict)
def obtener_estudiante(
    estudiante_id: int,
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener detalles de un estudiante específico - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Obtener estudiante {estudiante_id} | Usuario: {current_user.get('email')}")
        service = EstudianteService(db)
        estudiante = service.obtener_estudiante(estudiante_id)
        
        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        
        return success_response(
            data=estudiante,
            message="Estudiante obtenido exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=dict, status_code=201)
def crear_estudiante(
    estudiante_in: EstudianteCreate,
    current_user = Depends(permiso_requerido("crear_estudiante")),
    db: Session = Depends(get_db)
):
    """Crear nuevo estudiante - Requiere permiso 'crear_estudiante'"""
    try:
        service = EstudianteService(db)
        estudiante = service.crear_estudiante(estudiante_in)
        
        return success_response(
            data=estudiante,
            message="Estudiante creado exitosamente"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{estudiante_id}", response_model=dict)
def actualizar_estudiante(
    estudiante_id: int,
    estudiante_in: EstudianteUpdate,
    current_user = Depends(permiso_requerido("editar_estudiante")),
    db: Session = Depends(get_db)
):
    """Actualizar estudiante - Requiere permiso 'editar_estudiante'"""
    try:
        service = EstudianteService(db)
        estudiante = service.actualizar_estudiante(estudiante_id, estudiante_in)
        
        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        
        return success_response(
            data=estudiante,
            message="Estudiante actualizado exitosamente"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{estudiante_id}", response_model=dict)
def eliminar_estudiante(
    estudiante_id: int,
    current_user = Depends(permiso_requerido("eliminar_estudiante")),
    db: Session = Depends(get_db)
):
    """Eliminar estudiante - Requiere permiso 'eliminar_estudiante'"""
    try:
        service = EstudianteService(db)
        eliminado = service.eliminar_estudiante(estudiante_id)
        
        if not eliminado:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        
        return success_response(
            message="Estudiante eliminado exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
