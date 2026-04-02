from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Rol(BaseModel):
    __tablename__ = "roles"

    id_roles = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    permisos = Column(Text)
    descripcion = Column(Text)

    # relaciones
    usuarios = relationship("Usuario", back_populates="rol")
    permisos_rel = relationship("Permiso", secondary="rol_permiso", back_populates="roles")