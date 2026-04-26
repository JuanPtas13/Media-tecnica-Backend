from datetime import timedelta
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import (
    verify_password, 
    create_access_token, 
    get_current_user,
    hash_password
)
from app.services.usuario_service import UsuarioService
from app.schemas.auth import LoginRequest, TokenResponse, LoginResponse, UsuarioAutenticado
from app.utils.responses import success_response
from app.core.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Autenticación"])
settings = get_settings()


@router.post("/login", response_model=dict, status_code=200)
def login(
    credenciales: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint de login - Endpoint PÚBLICO
    
    Autentica un usuario con email y contraseña, retorna un JWT token.
    
    Args:
        credenciales: Email y contraseña del usuario
        db: Sesión de base de datos
        
    Returns:
        Token de acceso y datos del usuario autenticado
        
    Raises:
        HTTPException: 401 si las credenciales son inválidas
    """
    try:
        service = UsuarioService(db)
        usuario = service._obtener_por_correo_raw(credenciales.email)
        
        if not usuario:
            logger.warning(f"Intento de login con email no existente: {credenciales.email}")
            raise HTTPException(
                status_code=401, 
                detail="Email o contraseña incorrectos"
            )
        
        if not usuario.estado:
            logger.warning(f"Intento de login con usuario inactivo: {usuario.correo}")
            raise HTTPException(
                status_code=403, 
                detail="Usuario inactivo"
            )
        
        # Validar contraseña - manejo de errores de hash
        try:
            contraseña_valida = verify_password(credenciales.contraseña, usuario.contrasena_hash)
        except Exception as e:
            # Si el hash no es válido, tratar como credenciales inválidas
            logger.error(f"Error verificando contraseña para {usuario.correo}: {str(e)}")
            raise HTTPException(
                status_code=401, 
                detail="Email o contraseña incorrectos"
            )
        
        if not contraseña_valida:
            logger.warning(f"Intento de login con contraseña incorrecta: {usuario.correo}")
            raise HTTPException(
                status_code=401, 
                detail="Email o contraseña incorrectos"
            )
        
        # Crear JWT token con el ID del usuario Y su rol
        # El rol se incluye para que el frontend pueda verificarlo
        access_token = create_access_token(
            data={
                "sub": str(usuario.id_usuario),
                "rol": usuario.rol.nombre if usuario.rol else "usuario"
            },
            expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        )
        
        # Log de éxito
        logger.info(
            f"Login exitoso | Usuario: {usuario.correo} | "
            f"ID: {usuario.id_usuario} | Rol: {usuario.rol.nombre if usuario.rol else 'Sin rol'}"
        )
        
        # Retornar token y datos del usuario
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRATION_HOURS * 3600,
            "user": {
                "id": usuario.id_usuario,
                "email": usuario.correo,
                "nombre": usuario.nombre,
                "apellido1": usuario.apellido1,
                "apellido2": usuario.apellido2,
                "rol": usuario.rol.nombre if usuario.rol else None,
                "rol_id": usuario.rol_id,
                "estado": usuario.estado
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en login: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout", response_model=dict)
def logout(
    current_user = Depends(get_current_user)
):
    """
    Endpoint de logout - Requiere autenticación
    
    Nota: Con JWT stateless, el logout es principalmente del lado del cliente
    (descartar el token). Este endpoint solo sirve para auditoría o invalidación
    en base de datos si se implementa una lista negra de tokens.
    
    Args:
        current_user: Usuario autenticado (validado por get_current_user)
        
    Returns:
        Mensaje de confirmación
    """
    try:
        return success_response(
            message=f"Sesión de {current_user.get('nombre')} cerrada exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
