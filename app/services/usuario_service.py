from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.permiso_repository import PermisoRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.models.usuario import Usuario
from app.core.segurity import hash_password

logger = logging.getLogger(__name__)


class UsuarioService:
    """Servicio de lógica de negocio para Usuario"""
    
    def __init__(self, db: Session):
        self.repository = UsuarioRepository(db)
        self.permiso_repo = PermisoRepository(db)
    
    # ===== MÉTODOS INTERNOS (retornan modelo de base de datos) =====
    def _obtener_por_correo_raw(self, correo: str) -> Optional[Usuario]:
        """
        MÉTODO INTERNO: Obtener usuario por correo retornando el modelo de base de datos.
        Usado internamente cuando se necesita acceder a campos sensibles como contrasena_hash.
        NO retorna UsuarioResponse (sin contraseña).
        
        Args:
            correo: Email del usuario
            
        Returns:
            Modelo Usuario de base de datos o None
        """
        return self.repository.get_by_correo(correo)
    
    def _obtener_por_id_raw(self, usuario_id: int) -> Optional[Usuario]:
        """
        MÉTODO INTERNO: Obtener usuario por ID retornando el modelo de base de datos.
        Usado internamente cuando se necesita acceder a campos sensibles.
        NO retorna UsuarioResponse (sin contraseña).
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Modelo Usuario de base de datos o None
        """
        return self.repository.get_by_id(usuario_id)
    
    # ===== MÉTODOS PÚBLICOS (retornan UsuarioResponse para seguridad) =====
    
    def crear_usuario(self, usuario_in: UsuarioCreate) -> UsuarioResponse:
        """Crear nuevo usuario con validación y hash seguro de contraseña"""
        print(f"\n[SERVICE] ========== CREAR USUARIO: {usuario_in.correo} ==========")
        
        # PASO 1: Verificar correo único
        print(f"[SERVICE] PASO 1: Verificando correo único...")
        if self.repository.existe_correo(usuario_in.correo):
            error = f"Ya existe usuario con correo {usuario_in.correo}"
            print(f"[SERVICE] ERROR: {error}")
            raise ValueError(error)
        print(f"[SERVICE] OK: Correo disponible")
        
        # PASO 2: Convertir a diccionario y extraer contraseña
        print(f"[SERVICE] PASO 2: Extrayendo contraseña...")
        usuario_data = usuario_in.dict()
        password = usuario_data.pop("contrasena", None)
        print(f"[SERVICE] Contraseña extraída: {type(password).__name__}")
        
        if not password:
            error = "Contraseña requerida"
            print(f"[SERVICE] ERROR: {error}")
            raise ValueError(error)
        
        # PASO 3: Validar que sea string
        print(f"[SERVICE] PASO 3: Validando tipo de contraseña...")
        if not isinstance(password, str):
            error = f"Contraseña debe ser string, recibida: {type(password).__name__}"
            print(f"[SERVICE] ERROR: {error}")
            raise ValueError(error)
        print(f"[SERVICE] OK: Es string")
        
        # PASO 4: Verificar longitud
        print(f"[SERVICE] PASO 4: Verificando longitud...")
        chars = len(password)
        bytes_len = len(password.encode('utf-8'))
        print(f"[SERVICE] Contraseña: {chars} caracteres, {bytes_len} bytes UTF-8")
        
        if bytes_len > 72:
            error = f"Contraseña excede 72 bytes ({bytes_len} bytes)"
            print(f"[SERVICE] ERROR: {error}")
            raise ValueError(error)
        print(f"[SERVICE] OK: Dentro del límite")
        
        # PASO 5: Hashear
        print(f"[SERVICE] PASO 5: Ejecutando hash_password()...")
        try:
            usuario_data["contrasena_hash"] = hash_password(password)
            print(f"[SERVICE] OK: Contraseña hasheada")
        except Exception as e:
            error = f"Error hashing: {str(e)}"
            print(f"[SERVICE] ERROR: {error}")
            raise ValueError(error)
        
        # PASO 6: Guardar en BD
        print(f"[SERVICE] PASO 6: Guardando en base de datos...")
        try:
            usuario = self.repository.create(usuario_data)
            print(f"[SERVICE] OK: Usuario creado (ID: {usuario.id_usuario})")
            logger.info(f"Usuario creado: {usuario.correo} (ID: {usuario.id_usuario})")
            print(f"[SERVICE] ========== FIN CREATE_USUARIO ==========\n")
            return UsuarioResponse.from_orm(usuario)
        except Exception as e:
            error = f"Error guardando usuario: {str(e)}"
            print(f"[SERVICE] ERROR: {error}")
            raise ValueError(error)
            return UsuarioResponse.from_orm(usuario)
        except Exception as e:
            logger.error(f"Error al crear usuario en BD: {str(e)}")
            raise ValueError(f"Error al guardar el usuario: {str(e)}")
    
    def obtener_usuario(self, usuario_id: int) -> Optional[UsuarioResponse]:
        """Obtener usuario por ID"""
        usuario = self.repository.get_by_id(usuario_id)
        if not usuario:
            return None
        return UsuarioResponse.from_orm(usuario)
    
    def obtener_usuario_con_permisos(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener usuario por ID incluyendo sus permisos.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Diccionario con datos del usuario e incluye una lista de permisos
        """
        usuario = self.repository.get_by_id(usuario_id)
        if not usuario:
            return None
        
        permisos = self.permiso_repo.obtener_permisos_por_usuario(usuario_id)
        
        return {
            "id": usuario.id_usuario,
            "email": usuario.correo,
            "nombre": usuario.nombre,
            "apellido1": usuario.apellido1,
            "apellido2": usuario.apellido2,
            "rol": usuario.rol.nombre if usuario.rol else None,
            "rol_id": usuario.rol_id,
            "permisos": permisos,
            "estado": usuario.estado
        }
    
    def obtener_por_correo(self, correo: str) -> Optional[UsuarioResponse]:
        """Obtener usuario por correo"""
        usuario = self.repository.get_by_correo(correo)
        if not usuario:
            return None
        return UsuarioResponse.from_orm(usuario)
    
    def obtener_por_correo_con_permisos(self, correo: str) -> Optional[Dict[str, Any]]:
        """
        Obtener usuario por correo incluyendo sus permisos.
        
        Args:
            correo: Email del usuario
            
        Returns:
            Diccionario con datos del usuario e incluye una lista de permisos
        """
        usuario = self.repository.get_by_correo(correo)
        if not usuario:
            return None
        
        permisos = self.permiso_repo.obtener_permisos_por_usuario(usuario.id_usuario)
        
        return {
            "id": usuario.id_usuario,
            "email": usuario.correo,
            "nombre": usuario.nombre,
            "apellido1": usuario.apellido1,
            "apellido2": usuario.apellido2,
            "rol": usuario.rol.nombre if usuario.rol else None,
            "rol_id": usuario.rol_id,
            "permisos": permisos,
            "estado": usuario.estado
        }
    
    def obtener_todos(self, skip: int = 0, limit: int = 100) -> List[UsuarioResponse]:
        """Obtener todos los usuarios"""
        usuarios = self.repository.get_all(skip, limit)
        return [UsuarioResponse.from_orm(usr) for usr in usuarios]
    
    def cambiar_contrasena(self, usuario_id: int, nueva_contrasena: str) -> bool:
        """Cambiar contraseña de usuario hasheando la nueva"""
        usuario = self.repository.get_by_id(usuario_id)
        if not usuario:
            return False
    
        if not isinstance(nueva_contrasena, str) or len(nueva_contrasena.encode('utf-8')) > 72:
            raise ValueError("Contraseña inválida o excede 72 bytes")
    
        contrasena_hash = hash_password(nueva_contrasena)
        self.repository.update(usuario_id, {"contrasena_hash": contrasena_hash})
        return True
    
    def actualizar_usuario(self, usuario_id: int, usuario_in: UsuarioUpdate) -> Optional[UsuarioResponse]:
        """Actualizar usuario"""
        # Validar correo único si se está actualizando
        if usuario_in.correo:
            existente = self.repository.get_by_correo(usuario_in.correo)
            if existente and existente.id_usuario != usuario_id:
                raise ValueError(f"Ya existe otro usuario con correo {usuario_in.correo}")
        
        datos_actualizacion = {k: v for k, v in usuario_in.dict().items() if v is not None}
        
        usuario = self.repository.update(usuario_id, datos_actualizacion)
        if not usuario:
            return None
        
        return UsuarioResponse.from_orm(usuario)
    
    def eliminar_usuario(self, usuario_id: int) -> bool:
        """Eliminar usuario"""
        return self.repository.delete(usuario_id)
    
    def obtener_por_rol(self, rol_id: int, skip: int = 0, limit: int = 100) -> List[UsuarioResponse]:
        """Obtener usuarios por rol"""
        usuarios = self.repository.get_by_rol(rol_id, skip, limit)
        return [UsuarioResponse.from_orm(usr) for usr in usuarios]
    
    def obtener_activos(self, skip: int = 0, limit: int = 100) -> List[UsuarioResponse]:
        """Obtener usuarios activos"""
        usuarios = self.repository.get_activos(skip, limit)
        return [UsuarioResponse.from_orm(usr) for usr in usuarios]
