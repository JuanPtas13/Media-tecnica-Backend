from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Estudiante(BaseModel):
    __tablename__ = "estudiantes"

    id_estudiante = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellido1 = Column(String, nullable=False)
    apellido2 = Column(String, nullable=True)
    documento = Column(String, unique=True, nullable=False)
    
    grado_id = Column(Integer, ForeignKey("grado.id_grado"))  
    
    codigo_qr = Column(String, unique=True, nullable=True)
    estado = Column(Boolean, default=True)

    #  RELACIÓN (clave)
    grado = relationship("Grado", back_populates="estudiantes")

    #  RELACIÓN futura con registros
    registros = relationship("RegistroIngreso", back_populates="estudiante")

    def __repr__(self):
        return f"<Estudiante(id={self.id_estudiante}, nombre={self.nombre})>"