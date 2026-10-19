from sqlalchemy import Column, Integer, Date, Time, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


"""
Registro de ingreso del estudiante.

Cada fila representa un intento de registro (ingreso) con fecha, hora,
estado (a tiempo/tarde/ausente) y minutos de retraso calculados.
"""


class RegistroIngreso(BaseModel):
    __tablename__ = "registro_ingreso"

    # PK autoincremental
    id = Column(Integer, primary_key=True, index=True)

    # FKs a estudiante, usuario (quien registra) y config horaria usada
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id_estudiante"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id_usuario"))
    config_id = Column(Integer, ForeignKey("config_horario.id"))

    # Fecha y hora del registro
    fecha = Column(Date)
    hora = Column(Time)

    # Estado textual: 'a tiempo', 'tarde', 'ausente', etc.
    estado = Column(String)

    # Minutos de retraso calculados respecto al inicio de clase
    min_retraso = Column(Integer)

    # Relaciones ORM para acceder a objetos relacionados fácilmente
    estudiante = relationship("Estudiante", back_populates="registros")
    usuario = relationship("Usuario", back_populates="registros")
    config = relationship("ConfigHorario", back_populates="registros")