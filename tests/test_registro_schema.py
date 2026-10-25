from datetime import date, time
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.registro import RegistroIngresoCreate, RegistroIngresoResponse


def test_registro_response_accepts_missing_student_id():
    registro = SimpleNamespace(
        id=1,
        estudiante_id=None,
        usuario_id=2,
        config_id=3,
        fecha=date(2026, 10, 24),
        hora=time(8, 0),
        estado="a tiempo",
        min_retraso=None,
    )

    respuesta = RegistroIngresoResponse.model_validate(registro)

    assert respuesta.estudiante_id is None


def test_registro_create_still_requires_student_id():
    with pytest.raises(ValidationError):
        RegistroIngresoCreate.model_validate(
            {
                "usuario_id": 2,
                "config_id": 3,
                "fecha": date(2026, 10, 24),
                "hora": time(8, 0),
                "estado": "a tiempo",
            }
        )
