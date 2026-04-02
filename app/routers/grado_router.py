from typing import List
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import get_current_user, permiso_requerido, require_docente_or_admin
from app.services.grado_service import GradoService
from app.schemas.grado import GradoCreate, GradoUpdate, GradoResponse
from app.utils.responses import success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/grados", tags=["Grados"])


@router.get("/", response_model=dict)
def obtener_grados(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener lista de grados - DOCENTE o ADMIN"""
    try:
        logger.info(f"Listado de grados | Usuario: {current_user.get('email')} | Rol: {current_user.get('rol')}")
        service = GradoService(db)
        grados = service.obtener_todos(skip, limit)
        
        return success_response(
            data=grados,
            message="Grados obtenidos exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activos", response_model=dict)
def obtener_grados_activos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener grados activos - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Listado de grados activos | Usuario: {current_user.get('email')}")
        service = GradoService(db)
        grados = service.obtener_activos(skip, limit)
        
        return success_response(
            data=grados,
            message="Grados activos obtenidos exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/numero/{numero_grado}", response_model=dict)
def obtener_grados_por_numero(
    numero_grado: int,
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener grados por número - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Obtener grados por número {numero_grado} | Usuario: {current_user.get('email')}")
        service = GradoService(db)
        grados = service.obtener_por_numero(numero_grado)
        
        return success_response(
            data=grados,
            message=f"Se encontraron {len(grados)} grados"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{grado_id}", response_model=dict)
def obtener_grado(
    grado_id: int,
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener un grado específico - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Obtener grado {grado_id} | Usuario: {current_user.get('email')}")
        service = GradoService(db)
        grado = service.obtener_grado(grado_id)
        
        if not grado:
            raise HTTPException(status_code=404, detail="Grado no encontrado")
        
        return success_response(
            data=grado,
            message="Grado obtenido exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=dict, status_code=201)
def crear_grado(
    grado_in: GradoCreate,
    current_user = Depends(permiso_requerido("crear_grado")),
    db: Session = Depends(get_db)
):
    """Crear nuevo grado - Requiere permiso 'crear_grado'"""
    try:
        service = GradoService(db)
        grado = service.crear_grado(grado_in)
        
        return success_response(
            data=grado,
            message="Grado creado exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{grado_id}", response_model=dict)
def actualizar_grado(
    grado_id: int,
    grado_in: GradoUpdate,
    current_user = Depends(permiso_requerido("editar_grado")),
    db: Session = Depends(get_db)
):
    """Actualizar un grado - Requiere permiso 'editar_grado'"""
    try:
        service = GradoService(db)
        grado = service.actualizar_grado(grado_id, grado_in)
        
        if not grado:
            raise HTTPException(status_code=404, detail="Grado no encontrado")
        
        return success_response(
            data=grado,
            message="Grado actualizado exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{grado_id}", response_model=dict)
def eliminar_grado(
    grado_id: int,
    current_user = Depends(permiso_requerido("eliminar_grado")),
    db: Session = Depends(get_db)
):
    """Eliminar un grado - Requiere permiso 'eliminar_grado'"""
    try:
        service = GradoService(db)
        resultado = service.eliminar_grado(grado_id)
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Grado no encontrado")
        
        return success_response(
            data={},
            message="Grado eliminado exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
