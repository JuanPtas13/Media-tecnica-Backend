from pydantic import BaseModel


class RolPermisoBase(BaseModel):
    """Schema base para RolPermiso"""
    id_rol: int
    id_permiso: int


class RolPermisoCreate(RolPermisoBase):
    """Schema para crear una relación RolPermiso"""
    pass


class RolPermisoResponse(RolPermisoBase):
    """Schema de respuesta para RolPermiso"""
    id_rol_permiso: int
    
    class Config:
        from_attributes = True
