"""Crea el motor SQLAlchemy y proporciona sesiones por solicitud HTTP."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import get_settings

# Lee la URL desde el mismo origen de configuración utilizado por la API.
settings = get_settings()

# El motor administra las conexiones; SSL es obligatorio para PostgreSQL.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"sslmode": "require"}
)

# La fábrica crea una sesión independiente por operación o solicitud.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Los modelos heredan de esta base para registrarse en el metadata compartido.
Base = declarative_base()


def get_db() -> Session:
    """
    Proporciona una sesión temporal a FastAPI y siempre la cierra al finalizar.

    Uso: `db: Session = Depends(get_db)` en una ruta o dependencia.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
