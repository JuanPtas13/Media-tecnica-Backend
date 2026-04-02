from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Grado(BaseModel):
    __tablename__ = "grado"

    id_grado = Column(Integer, primary_key=True, index=True)
    numero_grado = Column(Integer, nullable=False)
    grupo = Column(String)
    estado = Column(Boolean, default=True)

    estudiantes = relationship("Estudiante", back_populates="grado")