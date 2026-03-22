from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.core.database import Base

class Estudiante(Base):
    __tablename__ = "estudiantes"

    id_estudiante = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    apellido1 = Column(String)
    apellido2 = Column(String)
    documento = Column(String)
    grado_id = Column(Integer, ForeignKey("grado.id_grado"))
    codigo_qr = Column(String)
    estado = Column(Boolean)
    activo = Column(Boolean)