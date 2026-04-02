from sqlalchemy import Column, Integer, Time, Date, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class ConfigHorario(BaseModel):
    __tablename__ = "config_horario"

    id = Column(Integer, primary_key=True, index=True)
    hora_inicio_clase = Column(Time, nullable=False)
    hora_limite_ingreso = Column(Time, nullable=False)
    min_tolerancia = Column(Integer)
    aplica_desde = Column(Date)
    aplica_hasta = Column(Date)
    estado = Column(Boolean, default=True)

    registros = relationship("RegistroIngreso", back_populates="config")