from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


"""
Modelo `Usuario`.

Representa la cuenta de acceso de una persona en el sistema. Contiene
los campos básicos (nombre, correo) y referencias al rol y registros
de asistencia asociados.
"""


class Usuario(BaseModel):
    __tablename__ = "usuarios"

    # Identificador primario del usuario
    id_usuario = Column(Integer, primary_key=True, index=True)

    # Datos personales básicos
    nombre = Column(String, nullable=False)
    apellido1 = Column(String)
    apellido2 = Column(String)

    # Correo único usado para login
    correo = Column(String, unique=True, nullable=False)

    # Hash de la contraseña almacenado (no guardar contraseñas en texto claro)
    contrasena_hash = Column(String, nullable=False)

    # FK al rol (admin/docente/vigilante/...) que determina permisos
    rol_id = Column(Integer, ForeignKey("roles.id_roles"))

    # Si la cuenta está activa o desactivada
    estado = Column(Boolean, default=True)

    # Relaciones ORM
    # Rol asociado (one-to-many desde Rol.usuarios)
    rol = relationship("Rol", back_populates="usuarios")

    # Registros de asistencia creados por este usuario (vigilante que registra)
    registros = relationship("RegistroIngreso", back_populates="usuario")