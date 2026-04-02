from typing import List
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import get_current_user, permiso_requerido, require_admin
from app.services.usuario_service import UsuarioService
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.utils.responses import success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/", response_model=dict)
def obtener_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Obtener lista de usuarios - SOLO ADMIN"""
    try:
        logger.info(f"Listado de usuarios | Usuario: {current_user.get('email')} | Rol: {current_user.get('rol')}")
        service = UsuarioService(db)
        usuarios = service.obtener_todos(skip, limit)
        
        return success_response(
            data=usuarios,
            message="Usuarios obtenidos exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activos", response_model=dict)
def obtener_usuarios_activos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Obtener usuarios activos - SOLO ADMIN"""
    try:
        logger.info(f"Listado de usuarios activos | Usuario: {current_user.get('email')} | Rol: {current_user.get('rol')}")
        service = UsuarioService(db)
        usuarios = service.obtener_activos(skip, limit)
        
        return success_response(
            data=usuarios,
            message="Usuarios activos obtenidos exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{usuario_id}", response_model=dict)
def obtener_usuario(
    usuario_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Obtener datos de un usuario específico - SOLO ADMIN"""
    try:
        logger.info(f"Obtener usuario {usuario_id} | Usuario: {current_user.get('email')} | Rol: {current_user.get('rol')}")
        service = UsuarioService(db)
        usuario = service.obtener_usuario(usuario_id)
        
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return success_response(
            data=usuario,
            message="Usuario obtenido exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=dict, status_code=201)
def crear_usuario(
    usuario_in: UsuarioCreate,
    current_user = Depends(permiso_requerido("crear_usuario")),
    db: Session = Depends(get_db)
):
    """Crear nuevo usuario - Requiere permiso 'crear_usuario'"""
    try:
        service = UsuarioService(db)
        usuario = service.crear_usuario(usuario_in)
        
        return success_response(
            data=usuario,
            message="Usuario creado exitosamente"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{usuario_id}", response_model=dict)
def actualizar_usuario(
    usuario_id: int,
    usuario_in: UsuarioUpdate,
    current_user = Depends(permiso_requerido("editar_usuario")),
    db: Session = Depends(get_db)
):
    """Actualizar usuario - Requiere permiso 'editar_usuario'"""
    try:
        service = UsuarioService(db)
        usuario = service.actualizar_usuario(usuario_id, usuario_in)
        
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return success_response(
            data=usuario,
            message="Usuario actualizado exitosamente"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{usuario_id}", response_model=dict)
def eliminar_usuario(
    usuario_id: int,
    current_user = Depends(permiso_requerido("eliminar_usuario")),
    db: Session = Depends(get_db)
):
    """Eliminar usuario - Requiere permiso 'eliminar_usuario'"""
    try:
        service = UsuarioService(db)
        eliminado = service.eliminar_usuario(usuario_id)
        
        if not eliminado:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return success_response(
            message="Usuario eliminado exitosamente"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
