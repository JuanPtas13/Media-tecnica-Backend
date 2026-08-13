from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


"""
Modelo `Estudiante`.

Contiene los datos del alumno, su documento único y la relación con el
grado y los registros de asistencia.
"""


class Estudiante(BaseModel):
    __tablename__ = "estudiantes"

    # PK del estudiante
    id_estudiante = Column(Integer, primary_key=True, index=True)

    # Nombres y apellidos obligatorios para identificación
    nombre = Column(String, nullable=False)
    apellido1 = Column(String, nullable=False)
    apellido2 = Column(String, nullable=True)

    # Documento (cédula o identificación) único por estudiante
    documento = Column(String, unique=True, nullable=False)
    
    # FK al grado al que pertenece el estudiante
    grado_id = Column(Integer, ForeignKey("grado.id_grado"))
    
    # Código QR opcional para escaneo rápido
    codigo_qr = Column(String, unique=True, nullable=True)

    # Estado activo/inactivo del estudiante
    estado = Column(Boolean, default=True)

    # Relación con Grado (many-to-one)
    grado = relationship("Grado", back_populates="estudiantes")

    # Registros de asistencia del estudiante (one-to-many)
    registros = relationship("RegistroIngreso", back_populates="estudiante")

    def __repr__(self):
        return f"<Estudiante(id={self.id_estudiante}, nombre={self.nombre})>"