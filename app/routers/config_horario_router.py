from typing import List
from datetime import date
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import get_current_user, permiso_requerido, require_docente_or_admin
from app.services.config_horario_service import ConfigHorarioService
from app.schemas.config_horario import ConfigHorarioCreate, ConfigHorarioUpdate, ConfigHorarioResponse
from app.utils.responses import success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config-horarios", tags=["Configuración Horaria"])


@router.get("/", response_model=dict)
def obtener_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener lista de configuraciones horarias - DOCENTE o ADMIN"""
    try:
        logger.info(f"Listado de configuraciones horarias | Usuario: {current_user.get('email')} | Rol: {current_user.get('rol')}")
        service = ConfigHorarioService(db)
        configs = service.obtener_todos(skip, limit)
        
        return success_response(
            data=configs,
            message="Configuraciones obtenidas exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activos", response_model=dict)
def obtener_configs_activos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener configuraciones horarias activas - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Listado de configuraciones horarias activas | Usuario: {current_user.get('email')}")
        service = ConfigHorarioService(db)
        configs = service.obtener_activos(skip, limit)
        
        return success_response(
            data=configs,
            message="Configuraciones activas obtenidas exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vigente", response_model=dict)
def obtener_config_vigente(
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener configuración vigente (activa en fecha actual) - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Obtener configuración vigente | Usuario: {current_user.get('email')}")
        service = ConfigHorarioService(db)
        config = service.obtener_vigente()
        
        if not config:
            raise HTTPException(status_code=404, detail="No hay configuración vigente")
        
        return success_response(
            data=config,
            message="Configuración vigente obtenida exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fecha/{fecha}", response_model=dict)
def obtener_config_en_fecha(
    fecha: date,
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener configuración para una fecha específica - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Obtener configuración para fecha {fecha} | Usuario: {current_user.get('email')}")
        service = ConfigHorarioService(db)
        config = service.obtener_en_fecha(fecha)
        
        if not config:
            raise HTTPException(status_code=404, detail="No hay configuración para esa fecha")
        
        return success_response(
            data=config,
            message="Configuración obtenida exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{config_id}", response_model=dict)
def obtener_config(
    config_id: int,
    current_user = Depends(require_docente_or_admin),
    db: Session = Depends(get_db)
):
    """Obtener una configuración específica - DOCENTE o ADMIN"""
    try:
        logger.debug(f"Obtener configuración {config_id} | Usuario: {current_user.get('email')}")
        service = ConfigHorarioService(db)
        config = service.obtener_config(config_id)
        
        if not config:
            raise HTTPException(status_code=404, detail="Configuración no encontrada")
        
        return success_response(
            data=config,
            message="Configuración obtenida exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=dict, status_code=201)
def crear_config(
    config_in: ConfigHorarioCreate,
    current_user = Depends(permiso_requerido("crear_config_horario")),
    db: Session = Depends(get_db)
):
    """Crear nueva configuración horaria - Requiere permiso 'crear_config_horario'"""
    try:
        service = ConfigHorarioService(db)
        config = service.crear_config(config_in)
        
        return success_response(
            data=config,
            message="Configuración creada exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{config_id}", response_model=dict)
def actualizar_config(
    config_id: int,
    config_in: ConfigHorarioUpdate,
    current_user = Depends(permiso_requerido("editar_config_horario")),
    db: Session = Depends(get_db)
):
    """Actualizar una configuración - Requiere permiso 'editar_config_horario'"""
    try:
        service = ConfigHorarioService(db)
        config = service.actualizar_config(config_id, config_in)
        
        if not config:
            raise HTTPException(status_code=404, detail="Configuración no encontrada")
        
        return success_response(
            data=config,
            message="Configuración actualizada exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{config_id}", response_model=dict)
def eliminar_config(
    config_id: int,
    current_user = Depends(permiso_requerido("eliminar_config_horario")),
    db: Session = Depends(get_db)
):
    """Eliminar una configuración - Requiere permiso 'eliminar_config_horario'"""
    try:
        service = ConfigHorarioService(db)
        resultado = service.eliminar_config(config_id)
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Configuración no encontrada")
        
        return success_response(
            data={},
            message="Configuración eliminada exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=dict)
def obtener_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de configuraciones horarias - Requiere autenticación"""
    try:
        service = ConfigHorarioService(db)
        configs = service.obtener_todos(skip, limit)
        
        return success_response(
            data=configs,
            message="Configuraciones obtenidas exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activos", response_model=dict)
def obtener_configs_activos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener configuraciones horarias activas - Requiere autenticación"""
    try:
        service = ConfigHorarioService(db)
        configs = service.obtener_activos(skip, limit)
        
        return success_response(
            data=configs,
            message="Configuraciones activas obtenidas exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vigente", response_model=dict)
def obtener_config_vigente(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener configuración vigente (activa en fecha actual) - Requiere autenticación"""
    try:
        service = ConfigHorarioService(db)
        config = service.obtener_vigente()
        
        if not config:
            raise HTTPException(status_code=404, detail="No hay configuración vigente")
        
        return success_response(
            data=config,
            message="Configuración vigente obtenida exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fecha/{fecha}", response_model=dict)
def obtener_config_en_fecha(
    fecha: date,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener configuración para una fecha específica - Requiere autenticación"""
    try:
        service = ConfigHorarioService(db)
        config = service.obtener_en_fecha(fecha)
        
        if not config:
            raise HTTPException(status_code=404, detail="No hay configuración para esa fecha")
        
        return success_response(
            data=config,
            message="Configuración obtenida exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{config_id}", response_model=dict)
def obtener_config(
    config_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener una configuración específica"""
    try:
        service = ConfigHorarioService(db)
        config = service.obtener_config(config_id)
        
        if not config:
            raise HTTPException(status_code=404, detail="Configuración no encontrada")
        
        return success_response(
            data=config,
            message="Configuración obtenida exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=dict, status_code=201)
def crear_config(
    config_in: ConfigHorarioCreate,
    db: Session = Depends(get_db)
):
    """Crear nueva configuración horaria"""
    try:
        service = ConfigHorarioService(db)
        config = service.crear_config(config_in)
        
        return success_response(
            data=config,
            message="Configuración creada exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{config_id}", response_model=dict)
def actualizar_config(
    config_id: int,
    config_in: ConfigHorarioUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una configuración"""
    try:
        service = ConfigHorarioService(db)
        config = service.actualizar_config(config_id, config_in)
        
        if not config:
            raise HTTPException(status_code=404, detail="Configuración no encontrada")
        
        return success_response(
            data=config,
            message="Configuración actualizada exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{config_id}", response_model=dict)
def eliminar_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar una configuración"""
    try:
        service = ConfigHorarioService(db)
        resultado = service.eliminar_config(config_id)
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Configuración no encontrada")
        
        return success_response(
            data={},
            message="Configuración eliminada exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
