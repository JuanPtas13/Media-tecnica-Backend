from app.core.database import SessionLocal
from app.models.estudiante import Estudiante

db = SessionLocal()

estudiantes = db.query(Estudiante).all()

for e in estudiantes:
    print(e.nombre, e.documento)
    
db.close()