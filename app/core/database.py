from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import get_settings

# Obtener configuración
settings = get_settings()

# Crear engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"sslmode": "require"}
)

# Crear SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para modelos
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency para obtener la sesión de base de datos
    Uso: def my_endpoint(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
