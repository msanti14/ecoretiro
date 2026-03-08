from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.core.config import settings

# Motor de conexión a PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para todos los modelos SQLAlchemy
class Base(DeclarativeBase):
    pass