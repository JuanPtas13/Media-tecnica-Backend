from sqlalchemy import Column, Integer, Date, Time, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class RegistroIngreso(BaseModel):
    __tablename__ = "registro_ingreso"

    id = Column(Integer, primary_key=True, index=True)

    estudiante_id = Column(Integer, ForeignKey("estudiantes.id_estudiante"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id_usuario"))
    config_id = Column(Integer, ForeignKey("config_horario.id"))

    fecha = Column(Date)
    hora = Column(Time)
    estado = Column(String)
    min_retraso = Column(Integer)

    estudiante = relationship("Estudiante", back_populates="registros")
    usuario = relationship("Usuario", back_populates="registros")
    config = relationship("ConfigHorario", back_populates="registros")