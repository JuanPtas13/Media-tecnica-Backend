from datetime import date, time
from types import SimpleNamespace
from unittest.mock import Mock

from app.repositories.reporte_service import ReporteRepository, _minutos_retraso
from app.services.registro_service import RegistroService


def test_asistencia_por_estudiante_incluye_minutos_de_retraso():
    """Conserva los minutos guardados para una entrada tardía."""
    registro = SimpleNamespace(
        id=1,
        fecha=date(2026, 10, 20),
        hora=time(8, 27),
        estado="tarde",
        estudiante_id=12,
        usuario_id=3,
        min_retraso=27,
        config=SimpleNamespace(hora_inicio_clase=time(8, 0)),
    )
    db = Mock()
    db.query.return_value.filter.return_value.all.return_value = [
        registro
    ]

    resultado = ReporteRepository(db).asistencia_por_estudiante(
        estudiante_id=12,
        fecha_inicio=date(2026, 10, 20),
        fecha_fin=date(2026, 10, 20),
    )

    assert resultado["registros"][0]["min_retraso"] == 27


def test_asistencia_por_estudiante_calcula_retraso_si_el_registro_no_lo_guardo():
    """Calcula el retraso usando el horario cuando no fue persistido."""
    registro = SimpleNamespace(
        id=1,
        fecha=date(2026, 10, 20),
        hora=time(8, 27),
        estado="tarde",
        estudiante_id=12,
        usuario_id=3,
        min_retraso=None,
        config=SimpleNamespace(hora_inicio_clase=time(8, 0)),
    )
    db = Mock()
    db.query.return_value.filter.return_value.all.return_value = [
        registro
    ]

    resultado = ReporteRepository(db).asistencia_por_estudiante(
        estudiante_id=12,
        fecha_inicio=date(2026, 10, 20),
        fecha_fin=date(2026, 10, 20),
    )

    assert resultado["registros"][0]["min_retraso"] == 27


def test_recalcula_retraso_tardio_guardado_incorrectamente_en_cero():
    """Corrige para el reporte una entrada tardía almacenada con cero minutos."""
    registro = SimpleNamespace(
        hora=time(8, 27),
        estado="tarde",
        min_retraso=0,
        config=SimpleNamespace(hora_inicio_clase=time(8, 0)),
    )

    assert _minutos_retraso(registro) == 27


def test_actividad_por_rango_incluye_detalle_de_registros():
    """Incluye los registros individuales junto con el total de actividad."""
    registro = SimpleNamespace(
        id=7,
        fecha=date(2026, 10, 20),
        hora=time(8, 27),
        estado="tarde",
        estudiante_id=12,
        min_retraso=27,
        config=SimpleNamespace(hora_inicio_clase=time(8, 0)),
    )
    estudiante = SimpleNamespace(
        nombre="Ana",
        apellido1="Pérez",
        apellido2="López",
        documento="123",
    )
    conteo_query = Mock()
    conteo_query.filter.return_value.scalar.return_value = 1
    registros_query = Mock()
    registros_query.join.return_value.filter.return_value.order_by.return_value.all.return_value = [
        (registro, estudiante)
    ]
    db = Mock()
    db.query.side_effect = [conteo_query, registros_query]

    resultado = ReporteRepository(db).actividad_por_rango(
        date(2026, 10, 20),
        date(2026, 10, 20),
    )

    assert resultado["total_registros"] == 1
    assert resultado["registros"][0]["estudiante"] == "Ana Pérez López"
    assert resultado["registros"][0]["min_retraso"] == 27


def test_registro_service_rechaza_registros_despues_del_cierre(monkeypatch):
    """Impide persistir entradas cuando el horario de asistencia ya cerró."""
    from app.repositories.config_horario_repository import ConfigHorarioRepository
    import app.services.registro_service as registro_service_module
    from datetime import datetime
    import pytest

    configuracion = SimpleNamespace(
        id=1,
        hora_cierre_asistencia=time(9, 0),
    )
    monkeypatch.setattr(
        ConfigHorarioRepository,
        "get_en_fecha",
        lambda self, fecha: configuracion,
    )

    class RelojFijo:
        @staticmethod
        def now():
            return datetime(2026, 10, 20, 20, 0)

    monkeypatch.setattr(registro_service_module, "datetime", RelojFijo)
    service = RegistroService(Mock())
    service.repository.create = Mock()
    registro = SimpleNamespace(config_id=1)

    with pytest.raises(ValueError, match="asistencia está cerrada"):
        service.crear_registro(registro)

    service.repository.create.assert_not_called()
"""Pruebas de retraso, reportes de actividad y cierre de registros de asistencia."""
