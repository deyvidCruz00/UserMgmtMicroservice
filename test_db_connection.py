#!/usr/bin/env python3
"""
Script para testear la conexión con la base de datos MySQL
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Cargar variables de entorno
load_dotenv()

def test_database_connection():
    """Testea la conexión con la base de datos"""
    print("=" * 50)
    print("TESTEANDO CONEXIÓN CON LA BASE DE DATOS")
    print("=" * 50)
    
    # Obtener URL de conexión
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        database_url = "mysql+pymysql://fastapi:fastapipass@127.0.0.1:3307/usermgmt_db"
        print("⚠️  Usando URL de fallback")
    
    print(f"📋 URL de conexión: {database_url}")
    print()
    
    try:
        # Crear engine
        print("🔧 Creando engine de SQLAlchemy...")
        engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        # Probar conexión básica
        print("🔌 Probando conexión básica...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Conexión básica exitosa")
        
        # Probar información del servidor
        print("📊 Obteniendo información del servidor...")
        with engine.connect() as connection:
            # Versión de MySQL
            result = connection.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            print(f"   - Versión MySQL: {version}")
            
            # Base de datos actual
            result = connection.execute(text("SELECT DATABASE()"))
            current_db = result.fetchone()[0]
            print(f"   - Base de datos actual: {current_db}")
            
            # Mostrar tablas existentes
            result = connection.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            if tables:
                print(f"   - Tablas encontradas: {len(tables)}")
                for table in tables:
                    print(f"     • {table[0]}")
            else:
                print("   - No se encontraron tablas")
        
        # Probar creación de tablas
        print("🏗️  Probando creación de tablas...")
        try:
            from app.models.customer import Customer, Base
            Base.metadata.create_all(bind=engine)
            print("✅ Tablas creadas/verificadas correctamente")
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
        
        # Probar operación CRUD básica
        print("🧪 Probando operación CRUD básica...")
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # Contar registros existentes
            from app.models.customer import Customer
            count = session.query(Customer).count()
            print(f"   - Registros existentes en customers: {count}")
        
        print()
        print("✅ TODAS LAS PRUEBAS EXITOSAS")
        print("🎉 La conexión con la base de datos está funcionando correctamente")
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Error de SQLAlchemy: {e}")
        return False
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que todos los módulos estén disponibles")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def check_environment():
    """Verifica la configuración del entorno"""
    print("🔍 VERIFICANDO CONFIGURACIÓN DEL ENTORNO")
    print("-" * 40)
    
    # Verificar archivo .env
    if os.path.exists('.env'):
        print("✅ Archivo .env encontrado")
    else:
        print("❌ Archivo .env no encontrado")
    
    # Verificar variables de entorno
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        print(f"✅ DATABASE_URL configurada: {database_url}")
    else:
        print("⚠️  DATABASE_URL no configurada, usando fallback")
    
    # Verificar dependencias
    try:
        import pymysql
        print("✅ PyMySQL disponible")
    except ImportError:
        print("❌ PyMySQL no encontrado")
    
    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy disponible (versión: {sqlalchemy.__version__})")
    except ImportError:
        print("❌ SQLAlchemy no encontrado")
    
    print()

if __name__ == "__main__":
    print("🚀 INICIANDO TEST DE CONEXIÓN A BASE DE DATOS")
    print()
    
    # Verificar entorno
    check_environment()
    
    # Testear conexión
    success = test_database_connection()
    
    if success:
        print("\n🎯 RESULTADO: Conexión exitosa")
        sys.exit(0)
    else:
        print("\n💥 RESULTADO: Conexión fallida")
        sys.exit(1)