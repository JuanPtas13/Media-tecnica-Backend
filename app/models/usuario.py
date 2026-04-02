from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Usuario(BaseModel):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellido1 = Column(String)
    apellido2 = Column(String)
    correo = Column(String, unique=True, nullable=False)
    contrasena_hash = Column(String, nullable=False)

    rol_id = Column(Integer, ForeignKey("roles.id_roles"))

    estado = Column(Boolean, default=True)

    # relaciones
    rol = relationship("Rol", back_populates="usuarios")
    registros = relationship("RegistroIngreso", back_populates="usuario")