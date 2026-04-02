from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.permiso_repository import PermisoRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.models.usuario import Usuario
from app.core.segurity import hash_password


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
        """Crear nuevo usuario"""
        # Validación: verificar correo único
        if self.repository.existe_correo(usuario_in.correo):
            raise ValueError(f"Ya existe un usuario con correo {usuario_in.correo}")
        
        usuario_data = usuario_in.dict()
        
        # OBLIGATORIO: Extraer contraseña SOLO en texto plano y eliminae del diccionario
        password = usuario_data.pop("contrasena", None)
        
        if not password:
            raise ValueError("La contraseña es requerida")
        
        # OBLIGATORIO: Validar que es string (no objeto, dict, o cualquier otra cosa)
        if not isinstance(password, str):
            raise ValueError(f"La contraseña debe ser texto plano (string), recibido: {type(password).__name__}")
        
        # DEBUG OBLIGATORIO: Detectar si se envía basura
        print("=" * 60)
        print("PASSWORD DEBUG:")
        print(f"  Valor: {password}")
        print(f"  Tipo: {type(password)}")
        print(f"  Longitud (caracteres): {len(password)}")
        print(f"  Longitud (bytes UTF-8): {len(password.encode('utf-8'))}")
        print("=" * 60)
        
        # OBLIGATORIO: Validar longitud REAL en bytes (bcrypt máximo 72 bytes)
        bytes_count = len(password.encode('utf-8'))
        if bytes_count > 72:
            raise ValueError(f"La contraseña supera el límite permitido (máximo 72 bytes, tiene {bytes_count} bytes)")
        
        # OBLIGATORIO: Hashear SOLO la contraseña en texto plano
        usuario_data["contrasena_hash"] = hash_password(password)
        
        usuario = self.repository.create(usuario_data)
        return UsuarioResponse.from_orm(usuario)
    
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
