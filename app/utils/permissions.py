"""
Módulo de utilidades para validación de permisos.
Proporciona funciones helper para verificar permisos en endpoints.
"""

from typing import Dict, Any, List, Optional, Callable
from functools import wraps
from fastapi import HTTPException, status


def tiene_permiso(user: Dict[str, Any], permiso: str) -> bool:
    """
    Verificar si un usuario tiene un permiso específico.
    
    Args:
        user: Diccionario del usuario con clave 'permisos'
        permiso: Nombre del permiso a verificar
        
    Returns:
        True si el usuario tiene el permiso, False en caso contrario
        
    Ejemplo:
        if not tiene_permiso(current_user, "crear_usuario"):
            raise HTTPException(status_code=403, detail="No autorizado")
    """
    if not user or "permisos" not in user:
        return False
    
    return permiso in user.get("permisos", [])


def tiene_alguno(user: Dict[str, Any], permisos: List[str]) -> bool:
    """
    Verificar si un usuario tiene al menos uno de los permisos especificados.
    
    Args:
        user: Diccionario del usuario con clave 'permisos'
        permisos: Lista de permisos para verificar (lógica OR)
        
    Returns:
        True si el usuario tiene al menos uno de los permisos
        
    Ejemplo:
        if not tiene_alguno(current_user, ["editar_usuario", "admin"]):
            raise HTTPException(status_code=403, detail="No autorizado")
    """
    if not user or "permisos" not in user:
        return False
    
    user_permisos = user.get("permisos", [])
    return any(p in user_permisos for p in permisos)


def tiene_todos(user: Dict[str, Any], permisos: List[str]) -> bool:
    """
    Verificar si un usuario tiene todos los permisos especificados.
    
    Args:
        user: Diccionario del usuario con clave 'permisos'
        permisos: Lista de permisos para verificar (lógica AND)
        
    Returns:
        True si el usuario tiene todos los permisos
        
    Ejemplo:
        if not tiene_todos(current_user, ["ver_estudiantes", "editar_estudiantes"]):
            raise HTTPException(status_code=403, detail="No autorizado")
    """
    if not user or "permisos" not in user:
        return False
    
    user_permisos = user.get("permisos", [])
    return all(p in user_permisos for p in permisos)


def requerir_permiso(permiso: str):
    """
    Decorador para requerir un permiso específico en un endpoint.
    Valida que el usuario (obtenido del parámetro 'current_user')
    tenga el permiso requerido.
    
    Args:
        permiso: Nombre del permiso requerido
        
    Raises:
        HTTPException: 403 Forbidden si el usuario no tiene el permiso
        
    Ejemplo:
        @router.post("/usuarios")
        @requerir_permiso("crear_usuario")
        def crear_usuario(current_user = Depends(get_current_user), db = Depends(get_db)):
            # Lógica protegida
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, current_user: Optional[Dict[str, Any]] = None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No autenticado"
                )
            
            if not tiene_permiso(current_user, permiso):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permiso requerido: {permiso}"
                )
            
            return func(*args, current_user=current_user, **kwargs)
        
        return wrapper
    return decorator


def requerir_alguno(permisos: List[str]):
    """
    Decorador para requerir al menos uno de los permisos especificados.
    Valida que el usuario (obtenido del parámetro 'current_user')
    tenga al menos uno de los permisos.
    
    Args:
        permisos: Lista de permisos (se requiere tener al menos uno)
        
    Raises:
        HTTPException: 403 Forbidden si el usuario no tiene ninguno de los permisos
        
    Ejemplo:
        @router.put("/usuarios/{id}")
        @requerir_alguno(["editar_usuario", "admin"])
        def actualizar_usuario(id: int, current_user = Depends(get_current_user)):
            # Lógica protegida
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, current_user: Optional[Dict[str, Any]] = None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No autenticado"
                )
            
            if not tiene_alguno(current_user, permisos):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Se requiere uno de estos permisos: {', '.join(permisos)}"
                )
            
            return func(*args, current_user=current_user, **kwargs)
        
        return wrapper
    return decorator


def requerir_todos(permisos: List[str]):
    """
    Decorador para requerir todos los permisos especificados.
    Valida que el usuario (obtenido del parámetro 'current_user')
    tenga todos los permisos.
    
    Args:
        permisos: Lista de permisos (debe tener todos)
        
    Raises:
        HTTPException: 403 Forbidden si el usuario no tiene todos los permisos
        
    Ejemplo:
        @router.delete("/usuarios/{id}")
        @requerir_todos(["eliminar_usuario", "admin"])
        def eliminar_usuario(id: int, current_user = Depends(get_current_user)):
            # Lógica protegida
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, current_user: Optional[Dict[str, Any]] = None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No autenticado"
                )
            
            if not tiene_todos(current_user, permisos):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Se requieren todos estos permisos: {', '.join(permisos)}"
                )
            
            return func(*args, current_user=current_user, **kwargs)
        
        return wrapper
    return decorator
