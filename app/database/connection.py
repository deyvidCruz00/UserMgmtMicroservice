import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Configuración de la base de datos desde variables de entorno
from dotenv import load_dotenv
load_dotenv()  # Asegurar que se cargan las variables de entorno

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback usando credenciales probadas
    DATABASE_URL = "mysql+pymysql://fastapi:fastapipass@localhost:3307/usermgmt_db"


# Crear el engine de SQLAlchemy
try:
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Cambiar a True para debug SQL
        pool_pre_ping=True,
        pool_recycle=300
    )
except Exception as e:
    print(f"Error creating database engine: {e}")
    raise

# Crear el SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obtener una sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    finally:
        db.close()


def create_tables():
    """
    Crear todas las tablas en la base de datos
    """
    try:
        from app.models.customer import Customer, Base
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise