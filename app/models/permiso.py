from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Permiso(BaseModel):
    __tablename__ = "permisos"

    id_permiso = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)
    descripcion = Column(Text)

    # relaciones
    roles = relationship("Rol", secondary="rol_permiso", back_populates="permisos_rel")
