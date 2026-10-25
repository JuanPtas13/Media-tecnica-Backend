from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import Estudiante, RegistroIngreso
from app.services.estudiante_service import EstudianteService


def test_eliminar_estudiante_elimina_sus_registros():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)

    try:
        with session_factory() as db:
            estudiante = Estudiante(
                nombre="Ana",
                apellido1="Pérez",
                documento="123",
            )
            db.add(estudiante)
            db.flush()
            estudiante_id = estudiante.id_estudiante

            db.add(
                RegistroIngreso(
                    estudiante_id=estudiante_id,
                    usuario_id=None,
                    config_id=None,
                    fecha=None,
                    hora=None,
                    estado=None,
                )
            )
            db.commit()

            assert EstudianteService(db).eliminar_estudiante(estudiante_id)
            assert db.query(Estudiante).filter_by(id_estudiante=estudiante_id).first() is None
            assert db.query(RegistroIngreso).filter_by(estudiante_id=estudiante_id).count() == 0
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
