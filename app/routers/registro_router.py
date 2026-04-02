from typing import List
from datetime import date
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import get_current_user, permiso_requerido, require_docente_or_admin, require_admin
from app.services.registro_service import RegistroService
from app.schemas.registro import RegistroIngresoCreate, RegistroIngresoUpdate, RegistroIngresoResponse
from app.utils.responses import success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/registros", tags=["Registros"])


@router.get("/", response_model=dict)
def obtener_registros(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener lista de registros - DOCENTE o ADMIN"""
    try:
        logger.info(f"Listado de registros | Usuario: {current_user.get('email')} | Rol: {current_user.get('rol')}")
        service = RegistroService(db)
        registros = service.obtener_todos(skip, limit)
        
        return success_response(
            data=registros,
            message="Registros obtenidos exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ultimos", response_model=dict)
def obtener_ultimos_registros(
    limite: int = Query(50, ge=1, le=500),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener los últimos registros - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Obtener últimos {limite} registros | Usuario: {current_user.get('email')}")
        service = RegistroService(db)
        registros = service.obtener_ultimos(limite)
        
        return success_response(
            data=registros,
            message=f"Se obtuvieron los últimos {len(registros)} registros"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estudiante/{estudiante_id}", response_model=dict)
def obtener_registros_estudiante(
    estudiante_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener registros de un estudiante - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Obtener registros del estudiante {estudiante_id} | Usuario: {current_user.get('email')}")
        service = RegistroService(db)
        registros = service.obtener_por_estudiante(estudiante_id, skip, limit)
        
        return success_response(
            data=registros,
            message=f"Se encontraron {len(registros)} registros"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usuario/{usuario_id}", response_model=dict)
def obtener_registros_usuario(
    usuario_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Obtener registros de un usuario (registrador) - SOLO ADMIN. Endpoint de auditoría."""
    try:
        logger.warning(f"AUDITERÍA: Solicitud de registros del usuario {usuario_id} | Usuario: {current_user.get('email')}")
        service = RegistroService(db)
        registros = service.obtener_por_usuario(usuario_id, skip, limit)
        
        return success_response(
            data=registros,
            message=f"Se encontraron {len(registros)} registros"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fecha/{fecha}", response_model=dict)
def obtener_registros_por_fecha(
    fecha: date,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener registros de una fecha específica - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Obtener registros de fecha {fecha} | Usuario: {current_user.get('email')}")
        service = RegistroService(db)
        registros = service.obtener_por_fecha(fecha, skip, limit)
        
        return success_response(
            data=registros,
            message=f"Se encontraron {len(registros)} registros para la fecha {fecha}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estado/{estado}", response_model=dict)
def obtener_registros_por_estado(
    estado: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener registros por estado - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Obtener registros con estado {estado} | Usuario: {current_user.get('email')}")
        service = RegistroService(db)
        registros = service.obtener_por_estado(estado, skip, limit)
        
        return success_response(
            data=registros,
            message=f"Se encontraron {len(registros)} registros con estado {estado}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{registro_id}", response_model=dict)
def obtener_registro(
    registro_id: int,
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener un registro específico - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Obtener registro {registro_id} | Usuario: {current_user.get('email')}")
        service = RegistroService(db)
        registro = service.obtener_registro(registro_id)
        
        if not registro:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        
        return success_response(
            data=registro,
            message="Registro obtenido exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=dict, status_code=201)
def crear_registro(
    registro_in: RegistroIngresoCreate,
    current_user = Depends(permiso_requerido("crear_registro")),
    db: Session = Depends(get_db)
):
    """Crear nuevo registro - Requiere permiso 'crear_registro'"""
    try:
        service = RegistroService(db)
        registro = service.crear_registro(registro_in)
        
        return success_response(
            data=registro,
            message="Registro creado exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{registro_id}", response_model=dict)
def actualizar_registro(
    registro_id: int,
    registro_in: RegistroIngresoUpdate,
    current_user = Depends(permiso_requerido("editar_registro")),
    db: Session = Depends(get_db)
):
    """Actualizar un registro - Requiere permiso 'editar_registro'"""
    try:
        service = RegistroService(db)
        registro = service.actualizar_registro(registro_id, registro_in)
        
        if not registro:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        
        return success_response(
            data=registro,
            message="Registro actualizado exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{registro_id}", response_model=dict)
def eliminar_registro(
    registro_id: int,
    current_user = Depends(permiso_requerido("eliminar_registro")),
    db: Session = Depends(get_db)
):
    """Eliminar un registro - Requiere permiso 'eliminar_registro'"""
    try:
        service = RegistroService(db)
        resultado = service.eliminar_registro(registro_id)
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        
        return success_response(
            data={},
            message="Registro eliminado exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        service = RegistroService(db)
        eliminado = service.eliminar_registro(registro_id)
        
        if not eliminado:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        
        return success_response(
            message="Registro eliminado exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
