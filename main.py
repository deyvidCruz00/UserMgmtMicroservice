import os
import uvicorn
import atexit
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers import customer
from app.database.connection import create_tables
from app.config.eureka import init_eureka, stop_eureka

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación FastAPI
app = FastAPI(
    title="User Management Microservice",
    description="Microservicio para la gestión de clientes del sistema",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(customer.router)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Intentar una consulta simple a la base de datos
        from app.database.connection import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "healthy",
            "service": "UserMgmtMicroservice",
            "message": "Service is up and running",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "service": "UserMgmtMicroservice",
            "message": f"Database connection failed: {str(e)}",
            "database": "disconnected"
        }

@app.get("/debug")
def debug_info():
    """Debug endpoint to check configuration"""
    import os
    return {
        "environment_variables": {
            "DB_HOST": os.getenv("DB_HOST", "NOT_SET"),
            "DB_PORT": os.getenv("DB_PORT", "NOT_SET"),
            "DB_NAME": os.getenv("DB_NAME", "NOT_SET"),
            "DB_USER": os.getenv("DB_USER", "NOT_SET"),
            "EUREKA_SERVER": os.getenv("EUREKA_SERVER", "NOT_SET"),
            "HOSTNAME": os.getenv("HOSTNAME", "NOT_SET")
        },
        "database_url_constructed": f"mysql+pymysql://{os.getenv('DB_USER')}:***@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    }

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación"""
    print("Starting User Management Microservice...")
    
    # Intentar crear tablas con reintentos
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            print(f"📊 Database connection attempt {attempt + 1}/{max_retries}")
            create_tables()
            print("✅ Database tables created successfully")
            break
            
        except Exception as e:
            print(f"❌ Database connection failed (attempt {attempt + 1}): {e}")
            
            if attempt < max_retries - 1:
                print(f"🔄 Retrying in {retry_delay} seconds...")
                import asyncio
                await asyncio.sleep(retry_delay)
                retry_delay += 5  # Incrementar delay para próximo intento
            else:
                print("❌ All database connection attempts failed")
                # Continuar sin base de datos para permitir health checks
    
    try:
        # Inicializar Eureka en thread separado para evitar bloqueo
        init_eureka()
        print("✅ Eureka client initialized successfully")
        
    except Exception as e:
        print(f"⚠️  Error initializing Eureka: {e}")
        # No fallar el startup si Eureka no está disponible

@app.on_event("shutdown") 
async def shutdown_event():
    """Evento que se ejecuta al cerrar la aplicación"""
    print("Shutting down User Management Microservice...")
    try:
        # Parar Eureka de forma segura
        stop_eureka()
        print("Eureka client stopped successfully")
    except Exception as e:
        print(f"Error during shutdown: {e}")
        # No fallar el shutdown por errores de Eureka

if __name__ == "__main__":
    # Obtener configuración del entorno
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"Starting server on {host}:{port}")
    
    # Registrar función de limpieza al salir
    atexit.register(stop_eureka)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )