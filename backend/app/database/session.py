"""
Configuración de sesión de base de datos
Contiene la configuración de SQLAlchemy, engine, SessionLocal y Base
"""

import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
if not os.path.exists(env_path):
    env_example_path = os.path.join(os.path.dirname(__file__), '../../.env.example')
    if os.path.exists(env_example_path):
        os.rename(env_example_path, env_path)
load_dotenv(env_path)

# Configuración de la base de datos
DB_DIR = os.path.join(os.path.dirname(__file__), '../db_sqlite')
os.makedirs(DB_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'hombres_lobo.db')}"

# Configuración SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency que provee una sesión de base de datos.
    Se puede usar directamente en funciones del core.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency de FastAPI que provee una sesión de base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()