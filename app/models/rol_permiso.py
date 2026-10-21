"""Modelo intermedio de la relación muchos-a-muchos entre roles y permisos."""

from sqlalchemy import Column, Integer, ForeignKey
from app.models.base import BaseModel


class RolPermiso(BaseModel):
    """Asocia una fila de rol con una fila de permiso en la base de datos."""

    __tablename__ = "rol_permiso"

    id_rol_permiso = Column(Integer, primary_key=True, index=True)
    id_rol = Column(Integer, ForeignKey("roles.id_roles"), nullable=False)
    id_permiso = Column(Integer, ForeignKey("permisos.id_permiso"), nullable=False)
