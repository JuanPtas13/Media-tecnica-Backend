from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres.lmxdctredhdwtmizhxor:ar$sf6#Fw8p?-hX@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}  
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()