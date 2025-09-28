import os
import logging
import asyncio
import threading
import time
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variable global para el cliente Eureka
eureka_client = None
eureka_thread: Optional[threading.Thread] = None
should_stop = False

class SimpleEurekaClient:
    """
    Cliente Eureka simplificado compatible con FastAPI
    """
    
    def __init__(self):
        self.eureka_server = os.getenv('EUREKA_SERVER', 'http://eureka-server:8761/eureka')
        self.service_name = "user-management-service"
        self.instance_host = os.getenv('HOSTNAME', 'user-service')
        self.instance_port = int(os.getenv('PORT', '8000'))
        self.instance_ip = os.getenv('HOST_IP', '127.0.0.1')
        self.heartbeat_interval = 30
        self.registered = False
        
    def register(self):
        """
        Registra el servicio en Eureka usando requests HTTP
        """
        try:
            import requests
            
            # Datos de registro
            registration_data = {
                "instance": {
                    "instanceId": f"{self.instance_host}:{self.service_name}:{self.instance_port}",
                    "hostName": self.instance_host,
                    "app": self.service_name.upper(),
                    "ipAddr": self.instance_ip,
                    "status": "UP",
                    "port": {"$": self.instance_port, "@enabled": "true"},
                    "healthCheckUrl": f"http://{self.instance_host}:{self.instance_port}/health",
                    "statusPageUrl": f"http://{self.instance_host}:{self.instance_port}/health",
                    "homePageUrl": f"http://{self.instance_host}:{self.instance_port}/",
                    "dataCenterInfo": {
                        "@class": "com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
                        "name": "MyOwn"
                    }
                }
            }
            
            # URL de registro
            register_url = f"{self.eureka_server}/apps/{self.service_name.upper()}"
            
            # Hacer petición de registro
            response = requests.post(
                register_url,
                json=registration_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Service registered successfully with Eureka: {self.service_name}")
                self.registered = True
                return True
            else:
                logger.error(f"❌ Failed to register with Eureka. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error registering with Eureka: {e}")
            return False
    
    def send_heartbeat(self):
        """
        Envía heartbeat a Eureka
        """
        if not self.registered:
            return False
            
        try:
            import requests
            
            # URL de heartbeat
            heartbeat_url = f"{self.eureka_server}/apps/{self.service_name.upper()}/{self.instance_host}:{self.service_name}:{self.instance_port}"
            
            response = requests.put(heartbeat_url, timeout=5)
            
            if response.status_code in [200, 204]:
                logger.debug(f"💓 Heartbeat sent successfully")
                return True
            else:
                logger.warning(f"⚠️  Heartbeat failed. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️  Error sending heartbeat: {e}")
            return False
    
    def deregister(self):
        """
        Desregistra el servicio de Eureka
        """
        if not self.registered:
            return True
            
        try:
            import requests
            
            # URL de desregistro
            deregister_url = f"{self.eureka_server}/apps/{self.service_name.upper()}/{self.instance_host}:{self.service_name}:{self.instance_port}"
            
            response = requests.delete(deregister_url, timeout=5)
            
            if response.status_code in [200, 204]:
                logger.info("✅ Service deregistered successfully from Eureka")
                self.registered = False
                return True
            else:
                logger.warning(f"⚠️  Deregistration failed. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️  Error deregistering from Eureka: {e}")
            return False

def eureka_worker():
    """
    Worker thread para manejar Eureka en segundo plano
    """
    global eureka_client, should_stop
    
    if not eureka_client:
        eureka_client = SimpleEurekaClient()
    
    # Intentar registrar con reintentos
    max_retries = 5
    for attempt in range(max_retries):
        if should_stop:
            return
            
        if eureka_client.register():
            break
        else:
            if attempt < max_retries - 1:
                logger.info(f"🔄 Retry registration in 10 seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(10)
            else:
                logger.error("❌ Failed to register after all attempts")
                return
    
    # Loop de heartbeat
    while not should_stop:
        time.sleep(eureka_client.heartbeat_interval)
        if not should_stop:
            eureka_client.send_heartbeat()

def init_eureka():
    """
    Inicializa el cliente Eureka en un thread separado
    """
    global eureka_thread, should_stop
    
    try:
        should_stop = False
        eureka_thread = threading.Thread(target=eureka_worker, daemon=True)
        eureka_thread.start()
        
        logger.info("🚀 Eureka client started in background thread")
        
    except Exception as e:
        logger.error(f"❌ Error starting Eureka client: {e}")
        raise e

def stop_eureka():
    """
    Para el cliente Eureka de forma segura
    """
    global eureka_client, eureka_thread, should_stop
    
    try:
        should_stop = True
        
        # Desregistrar si está registrado
        if eureka_client and eureka_client.registered:
            eureka_client.deregister()
        
        # Esperar que termine el thread
        if eureka_thread and eureka_thread.is_alive():
            eureka_thread.join(timeout=5)
        
        logger.info("✅ Eureka client stopped successfully")
        
    except Exception as e:
        logger.error(f"⚠️  Error stopping Eureka client: {e}")
        # No re-lanzar la excepción para evitar problemas en shutdown