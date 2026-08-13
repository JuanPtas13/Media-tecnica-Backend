from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


"""
Modelo `Rol`.

Define un rol del sistema (admin, docente, vigilante, etc.) y su descripción.
También mantiene una relación many-to-many con permisos.
"""


class Rol(BaseModel):
    __tablename__ = "roles"

    id_roles = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)

    # Campo que puede almacenar una lista serializada de permisos (opcional)
    permisos = Column(Text)
    descripcion = Column(Text)

    # relaciones
    usuarios = relationship("Usuario", back_populates="rol")

    # Relación many-to-many con Permiso a través de la tabla rol_permiso
    permisos_rel = relationship("Permiso", secondary="rol_permiso", back_populates="roles")