from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')


class ResponseBase(BaseModel, Generic[T]):
    """Respuesta estándar para todos los endpoints"""
    
    success: bool
    message: str
    data: Optional[T] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operación exitosa",
                "data": None
            }
        }


class ResponseSuccess(ResponseBase[T]):
    """Respuesta exitosa"""
    
    def __init__(self, message: str = "Operación exitosa", data: Optional[T] = None, **kwargs):
        super().__init__(success=True, message=message, data=data, **kwargs)


class ResponseError(ResponseBase):
    """Respuesta de error"""
    
    def __init__(self, message: str = "Error en la operación", **kwargs):
        super().__init__(success=False, message=message, data=None, **kwargs)


def success_response(data: Any = None, message: str = "Operación exitosa") -> dict:
    """Crear respuesta de éxito"""
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(message: str = "Error en la operación") -> dict:
    """Crear respuesta de error"""
    return {
        "success": False,
        "message": message,
        "data": None
    }
