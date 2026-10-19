from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


"""
Modelo `Grado`.

Representa un grado escolar (ej. 10-A) y relaciona los estudiantes que pertenecen a él.
"""


class Grado(BaseModel):
    __tablename__ = "grado"

    # PK del grado
    id_grado = Column(Integer, primary_key=True, index=True)

    # Número del grado (ej. 10) y grupo (ej. A)
    numero_grado = Column(Integer, nullable=False)
    grupo = Column(String)

    # Estado activo/inactivo (para ocultar años escolares anteriores)
    estado = Column(Boolean, default=True)

    # Lista de estudiantes que pertenecen a este grado
    estudiantes = relationship("Estudiante", back_populates="grado")