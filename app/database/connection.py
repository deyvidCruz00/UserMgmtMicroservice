import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Configuración de la base de datos desde variables de entorno
from dotenv import load_dotenv
load_dotenv()  # Asegurar que se cargan las variables de entorno

# Obtener variables de entorno (siempre disponibles)
DB_USER = os.getenv("DB_USER", "fastapi")
DB_PASSWORD = os.getenv("DB_PASSWORD", "fastapipass") 
DB_HOST = os.getenv("DB_HOST", "mysql")  # Cambiar default a 'mysql' (nombre del contenedor)
DB_PORT = os.getenv("DB_PORT", "3307")
DB_NAME = os.getenv("DB_NAME", "usermgmt_db")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Construir URL desde variables de entorno individuales
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"Conectando a base de datos: {DATABASE_URL}")
print(f"Variables de entorno - Host: {DB_HOST}, User: {DB_USER}, DB: {DB_NAME}")


# Crear el engine de SQLAlchemy
try:
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Cambiar a True para debug SQL
        pool_pre_ping=True,
        pool_recycle=3600,  # Reciclar conexiones cada hora
        connect_args={
            "connect_timeout": 60,  # Timeout de conexión aumentado
            "charset": "utf8mb4"
        }
    )
    print(f"✅ Database engine created successfully")
except Exception as e:
    print(f"❌ Error creating database engine: {e}")
    print(f"Database URL: {DATABASE_URL}")
    print(f"Error type: {type(e)}")
    
    # Intentar conexión simple para diagnóstico
    try:
        import pymysql
        DB_HOST = os.getenv("DB_HOST", "mysql")
        DB_PORT = os.getenv("DB_PORT", "3306") 
        DB_USER = os.getenv("DB_USER", "fastapi")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "fastapipass")
        DB_NAME = os.getenv("DB_NAME", "usermgmt_db")
        
        print(f"🔍 Testing direct connection to {DB_HOST}:{DB_PORT}")
        conn = pymysql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connect_timeout=10
        )
        conn.close()
        print("✅ Direct PyMySQL connection successful")
    except Exception as direct_error:
        print(f"❌ Direct connection also failed: {direct_error}")
    raise e

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