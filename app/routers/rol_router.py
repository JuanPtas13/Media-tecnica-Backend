import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import require_admin
from app.services.rol_service import RolService
from app.utils.responses import success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=dict)
def obtener_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Obtener lista de roles - SOLO ADMIN"""
    try:
        logger.info(f"Listado de roles | Usuario: {current_user.get('email')} | Rol: {current_user.get('rol')}")
        service = RolService(db)
        roles = service.obtener_todos(skip, limit)
        
        return success_response(
            data=roles,
            message="Roles obtenidos exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nombre/{nombre}", response_model=dict)
def obtener_rol_por_nombre(
    nombre: str,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Obtener un rol por nombre - SOLO ADMIN"""
    try:
        logger.debug(f"Obtener rol por nombre: {nombre} | Usuario: {current_user.get('email')}")
        service = RolService(db)
        rol = service.obtener_por_nombre(nombre)
        
        if not rol:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        
        return success_response(
            data=rol,
            message="Rol obtenido exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/buscar", response_model=dict)
def buscar_roles(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Buscar roles por nombre - SOLO ADMIN"""
    try:
        logger.debug(f"Buscar roles: {query} | Usuario: {current_user.get('email')}")
        service = RolService(db)
        roles = service.buscar(query, skip, limit)
        
        return success_response(
            data=roles,
            message=f"Se encontraron {len(roles)} roles"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{rol_id}", response_model=dict)
def obtener_rol(
    rol_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Obtener un rol específico - SOLO ADMIN"""
    try:
        logger.debug(f"Obtener rol {rol_id} | Usuario: {current_user.get('email')}")
        service = RolService(db)
        rol = service.obtener_rol(rol_id)
        
        if not rol:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        
        return success_response(
            data=rol,
            message="Rol obtenido exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
