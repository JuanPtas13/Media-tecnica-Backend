from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
import time
import bcrypt
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.database import get_db
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.permiso_repository import PermisoRepository
from app.utils.permissions import tiene_permiso

# Configurar logger
logger = logging.getLogger(__name__)

# Configuración
settings = get_settings()

# Configuración HTTP Bearer - Sin tokenUrl, solo para validar tokens Bearer
http_bearer = HTTPBearer(
    description="Ingresa tu JWT token Bearer para autenticación"
)



def hash_password(password: str) -> str:
    """
    Hashear una contraseña usando bcrypt directamente.
    
    ⚠️ CRÍTICO: bcrypt tiene límite DURO de 72 bytes.
    
    Args:
        password: Contraseña en texto plano (string)
        
    Returns:
        Hash bcrypt de la contraseña (bytes decodificado a string)
        
    Raises:
        ValueError: Si hay error al hashear
    """
    print("[HASH] ====== INICIANDO HASH_PASSWORD ======")
    print(f"[HASH] Tipo entrada: {type(password)}")
    print(f"[HASH] Valor recibido: {password[:10]}..." if len(password) > 10 else f"[HASH] Valor recibido: {password}")
    print(f"[HASH] Caracteres: {len(password)}")
    print(f"[HASH] Bytes UTF-8: {len(password.encode('utf-8'))}")
    
    # VALIDACIÓN 1: Debe ser string
    if not isinstance(password, str):
        print(f"[HASH] ERROR: No es string, es {type(password).__name__}")
        logger.error(f"hash_password recibió tipo incorrecto: {type(password).__name__}")
        raise ValueError(f"La contraseña debe ser string, recibido: {type(password).__name__}")
    
    # VALIDACIÓN 2: No puede exceder 72 bytes en UTF-8
    bytes_length = len(password.encode('utf-8'))
    if bytes_length > 72:
        print(f"[HASH] ERROR: {bytes_length} bytes > 72 bytes")
        logger.error(f"Contraseña excede 72 bytes: {bytes_length} bytes")
        raise ValueError(
            f"Contraseña demasiado larga ({bytes_length} bytes, máximo 72). "
            f"Usa una contraseña más corta."
        )
    
    # VALIDACIÓN 3: Intentar hashear directamente con bcrypt
    try:
        print(f"[HASH] Usando bcrypt.hashpw() directamente...")
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        hashed_str = hashed_bytes.decode('utf-8')
        print(f"[HASH] ✓ Éxito - Hash de {len(hashed_str)} caracteres")
        logger.info("Contraseña hasheada correctamente con bcrypt")
        return hashed_str
        
    except ValueError as e:
        print(f"[HASH] ERROR ValueError: {str(e)}")
        logger.error(f"Error bcrypt: {str(e)}")
        raise ValueError(f"Error al procesar contraseña: {str(e)}")
    except Exception as e:
        print(f"[HASH] ERROR inesperado: {type(e).__name__}: {str(e)}")
        logger.error(f"Error inesperado al hashear: {type(e).__name__}: {str(e)}")
        raise ValueError(f"Error procesando contraseña: {str(e)}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar una contraseña contra su hash usando bcrypt directamente"""
    try:
        print(f"[VERIFY] Comparando contraseña...")
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        result = bcrypt.checkpw(plain_bytes, hashed_bytes)
        print(f"[VERIFY] Resultado: {result}")
        return result
    except Exception as e:
        print(f"[VERIFY] Error: {str(e)}")
        logger.error(f"Error verificando contraseña: {str(e)}")
        return False



def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear un JWT token.
    
    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        Token JWT en formato string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    # IMPORTANTE: Convertir datetime a timestamp Unix (segundos desde epoch)
    # jwt.encode requiere un número entero, no un datetime
    expire_timestamp = int(expire.timestamp())
    to_encode.update({"exp": expire_timestamp})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodificar un JWT token con manejo detallado de errores específicos.
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        Payload del token decodificado
        
    Raises:
        ExpiredSignatureError: Si el token ha expirado
        JWTClaimsError: Si los reclamos (claims) del JWT son inválidos
        JWTError: Si el token es inválido, malformado, o firma incorrecta
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        logger.debug(f"Token decodificado exitosamente. Sub: {payload.get('sub')}, Exp: {payload.get('exp')}")
        return payload
        
    except ExpiredSignatureError as e:
        logger.warning("Intento de acceso con token expirado")
        raise
        
    except JWTClaimsError as e:
        logger.warning(f"Reclamo JWT inválido: {str(e)}")
        raise
        
    except JWTError as e:
        error_msg = str(e)
        if "Signature verification failed" in error_msg:
            logger.error("Token con firma inválida (clave incorrecta)")
        elif "Invalid token" in error_msg or "Malformed" in error_msg:
            logger.warning("Token malformado o inválido")
        else:
            logger.error(f"Error en decodificación de JWT: {error_msg}")
        raise


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtener el usuario actual desde el JWT token Bearer.
    Incluye los permisos del usuario desde la base de datos.
    
    Args:
        credentials: Credenciales HTTP Bearer (token automáticamente extraído del header)
        db: Sesión de base de datos
        
    Returns:
        Diccionario con datos del usuario incluyendo permisos
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    return get_current_user_from_token(credentials.credentials, db)


def get_current_user_from_token(
    token: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtener el usuario actual desde el JWT token.
    Incluye los permisos del usuario desde la base de datos.
    
    Proporciona mensajes de error específicos para cada tipo de fallo de autenticación.
    
    Args:
        token: Token JWT
        db: Sesión de base de datos
        
    Returns:
        Diccionario con datos del usuario incluyendo permisos
        
    Raises:
        HTTPException: Con código y mensaje específico según el tipo de error
    """
    # ========== VALIDACIÓN 1: Token vacío ==========
    if not token:
        logger.warning("Intento de acceso sin token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token requerido - No se encontró token en el header Authorization",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ========== VALIDACIÓN 2: Decodificar token ==========
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        logger.warning("Intento de acceso con token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado - Por favor, inicia sesión de nuevo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTClaimsError as e:
        logger.warning(f"Reclamo JWT inválido: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token contiene reclamos inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.warning(f"Token inválido/malformado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o no pudo ser decodificado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ========== VALIDACIÓN 3: Payload vacío ==========
    if payload is None:
        logger.error("Payload del token es vacío después de decodificación")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Payload del token está vacío",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ========== VALIDACIÓN 4: Campo 'sub' presente ==========
    usuario_id_raw = payload.get("sub")
    if usuario_id_raw is None:
        logger.error(f"Campo 'sub' faltante en payload. Campos disponibles: {list(payload.keys())}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Campo 'sub' (usuario ID) faltante en token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ========== VALIDACIÓN 5: Convertir 'sub' a int ==========
    try:
        usuario_id: int = int(usuario_id_raw) if isinstance(usuario_id_raw, str) else usuario_id_raw
        logger.debug(f"Usuario ID extraído del payload: {usuario_id}")
    except (ValueError, TypeError) as e:
        logger.error(f"No se puede convertir 'sub' a int. Valor: {usuario_id_raw}, Tipo: {type(usuario_id_raw).__name__}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Campo 'sub' en token tiene formato incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ========== VALIDACIÓN 6: Usuario existe en BD ==========
    usuario_repo = UsuarioRepository(db)
    usuario = usuario_repo.get_by_id(usuario_id)
    
    if usuario is None:
        logger.warning(f"Usuario no existe en BD. ID: {usuario_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado en la base de datos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ========== VALIDACIÓN 7: Usuario activo ==========
    if not usuario.estado:
        logger.warning(f"Intento de acceso con usuario inactivo: {usuario.correo}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo - Contacta con el administrador"
        )
    
    # ========== ÉXITO: Obtener permisos ==========
    permiso_repo = PermisoRepository(db)
    permisos = permiso_repo.obtener_permisos_por_usuario(usuario_id)
    
    # Construir objeto de usuario con permisos
    user_data = {
        "id": usuario.id_usuario,
        "email": usuario.correo,
        "nombre": usuario.nombre,
        "apellido1": usuario.apellido1,
        "apellido2": usuario.apellido2,
        "rol": usuario.rol.nombre if usuario.rol else None,
        "rol_id": usuario.rol_id,
        "permisos": permisos
    }
    
    logger.info(
        f"✅ AUTENTICACIÓN EXITOSA | "
        f"Email: {usuario.correo} | "
        f"Rol: {usuario.rol.nombre if usuario.rol else 'Sin rol'} | "
        f"Permisos: {len(permisos)} | "
        f"ID: {usuario.id_usuario}"
    )
    
    return user_data


def permiso_requerido(permiso: str):
    """
    Crea una dependencia que valida que el usuario tenga un permiso específico.
    Se utiliza con Depends() en los endpoints.
    
    Args:
        permiso: Nombre del permiso requerido
        
    Returns:
        Una función de dependencia que retorna el usuario autenticado
        
    Raises:
        HTTPException: 401 si no está autenticado, 403 si no tiene el permiso
        
    Ejemplo:
        @router.post("/usuarios")
        def crear_usuario(
            usuario_in: UsuarioCreate,
            current_user = Depends(permiso_requerido("crear_usuario")),
            db: Session = Depends(get_db)
        ):
            # current_user está disponible y garantiza que tiene el permiso
            pass
    """
    async def check_permission(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        """
        Verifica que el usuario tenga el permiso requerido.
        
        Args:
            current_user: Usuario obtenido de get_current_user
            
        Returns:
            El usuario si tiene el permiso
            
        Raises:
            HTTPException: 403 si no tiene el permiso
        """
        if not tiene_permiso(current_user, permiso):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso requerido: {permiso}"
            )
        return current_user
    
    return check_permission


# ============================================================================
# DEPENDENCIAS DE AUTORIZACIÓN POR ROL
# ============================================================================
# Sistema de autorización basado en roles reutilizable y escalable
# ============================================================================

def require_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependencia que requiere rol de ADMIN.
    
    Uso:
        @router.delete("/usuarios/{id}")
        def eliminar_usuario(
            id: int,
            current_user = Depends(require_admin),
            db: Session = Depends(get_db)
        ):
            # Código aquí garantiza que es ADMIN
            pass
    
    Args:
        current_user: Usuario autenticado obtenido de get_current_user
        
    Returns:
        El usuario si tiene rol admin
        
    Raises:
        HTTPException: 403 si no es admin
    """
    user_role = current_user.get("rol")
    user_email = current_user.get("email")
    
    if user_role != "admin":
        logger.warning(
            f"🔴 ACCESO DENEGADO - ROL INSUFICIENTE | "
            f"Email: {user_email} | Rol actual: {user_role} | Se requiere: admin"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado. Se requiere rol: admin"
        )
    
    logger.debug(f"✅ ACCESO PERMITIDO (ADMIN) | Email: {user_email}")
    return current_user


def require_docente(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependencia que requiere rol de DOCENTE.
    
    Uso:
        @router.post("/registros/calificaciones")
        def actualizar_calificaciones(
            data: dict,
            current_user = Depends(require_docente),
            db: Session = Depends(get_db)
        ):
            # Código aquí garantiza que es DOCENTE o superior (ADMIN)
            pass
    
    Args:
        current_user: Usuario autenticado obtenido de get_current_user
        
    Returns:
        El usuario si tiene rol docente o admin
        
    Raises:
        HTTPException: 403 si no es docente
    """
    rol_usuario = current_user.get("rol")
    
    # Permitir ADMIN acceso a endpoints de DOCENTE
    if rol_usuario not in ["docente", "admin"]:
        logger.warning(f"Acceso denegado - se requiere DOCENTE. Usuario: {current_user.get('email')}, Rol: {rol_usuario}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado. Se requiere rol: docente"
        )
    return current_user


def require_vigilante(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependencia que requiere rol de VIGILANTE.
    
    Uso:
        @router.post("/registros")
        def crear_registro(
            registro: RegistroCreate,
            current_user = Depends(require_vigilante),
            db: Session = Depends(get_db)
        ):
            # Código aquí garantiza que es VIGILANTE o superior (ADMIN)
            pass
    
    Args:
        current_user: Usuario autenticado obtenido de get_current_user
        
    Returns:
        El usuario si tiene rol vigilante o admin
        
    Raises:
        HTTPException: 403 si no es vigilante
    """
    rol_usuario = current_user.get("rol")
    
    # Permitir ADMIN acceso a endpoints de VIGILANTE
    if rol_usuario not in ["vigilante", "admin"]:
        logger.warning(f"Acceso denegado - se requiere VIGILANTE. Usuario: {current_user.get('email')}, Rol: {rol_usuario}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado. Se requiere rol: vigilante"
        )
    return current_user


def require_docente_or_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependencia que requiere rol de DOCENTE o ADMIN.
    Útil cuando ambos roles necesitan acceso.
    
    Args:
        current_user: Usuario autenticado obtenido de get_current_user
        
    Returns:
        El usuario si tiene rol docente o admin
        
    Raises:
        HTTPException: 403 si no es docente o admin
    """
    rol_usuario = current_user.get("rol")
    
    if rol_usuario not in ["docente", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado. Se requiere rol: docente o admin"
        )
    return current_user


def require_no_vigilante(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependencia que NIEGA acceso específicamente a VIGILANTES.
    Útil para endpoints que docente y admin pueden acceder pero vigilante no.
    
    Args:
        current_user: Usuario autenticado obtenido de get_current_user
        
    Returns:
        El usuario si NO es vigilante
        
    Raises:
        HTTPException: 403 si es vigilante
    """
    rol_usuario = current_user.get("rol")
    
    if rol_usuario == "vigilante":
        logger.warning(f"Acceso denegado para VIGILANTE. Usuario: {current_user.get('email')}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los vigilantes no tienen acceso a este recurso"
        )
    return current_user
