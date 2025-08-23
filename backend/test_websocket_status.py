#!/usr/bin/env python3
"""
Script de prueba para WebSockets con gestión de estado de usuarios.
Demuestra la integración de cambios de estado automáticos y manuales vía WebSocket.
"""

import asyncio
import websockets
import json
import requests
import os
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

# Crear un nombre único para evitar conflictos
unique_suffix = str(int(time.time()))
TEST_USER = {
    "username": f"test_ws_user_{unique_suffix}",
    "email": f"test_ws_{unique_suffix}@example.com",
    "password": "testpassword123"
}

class WebSocketTester:
    def __init__(self):
        self.user_token = None
        self.user_id = None
        self.game_id = "test_game_123"
        self.websocket = None
    
    async def setup_user(self):
        """Registrar y hacer login del usuario de prueba"""
        print("🔧 Configurando usuario de prueba...")
        
        # Registrar usuario
        register_response = requests.post(
            f"{BASE_URL}/register",
            data={
                "username": TEST_USER["username"],
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )
        
        if register_response.status_code in [200, 201]:
            print("✅ Usuario registrado exitosamente")
            user_data = register_response.json()
            self.user_id = user_data["user"]["id"]
        else:
            print(f"❌ Error al registrar usuario: {register_response.text}")
            return False
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/login",
            data={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        )
        
        if login_response.status_code == 200:
            print("✅ Login exitoso")
            token_data = login_response.json()
            self.user_token = token_data["access_token"]
            return True
        else:
            print(f"❌ Error en login: {login_response.text}")
            return False
    
    async def connect_websocket(self):
        """Conectar al WebSocket"""
        print(f"\n🔌 Conectando al WebSocket del juego {self.game_id}...")
        
        try:
            ws_url = f"{WS_URL}/ws/{self.game_id}?token={self.user_token}"
            self.websocket = await websockets.connect(ws_url)
            print("✅ Conectado al WebSocket")
            return True
        except Exception as e:
            print(f"❌ Error conectando al WebSocket: {e}")
            return False
    
    async def listen_messages(self):
        """Escuchar mensajes del WebSocket"""
        print("👂 Iniciando escucha de mensajes...")
        
        if not self.websocket:
            print("❌ WebSocket no está conectado")
            return
            
        try:
            while True:
                message = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
                data = json.loads(message)
                
                # Filtrar mensajes relevantes
                msg_type = data.get("type")
                if msg_type in ["user_status_changed", "success", "error"]:
                    print(f"📨 Mensaje recibido: {json.dumps(data, indent=2)}")
                elif msg_type == "system_message":
                    print(f"💬 Sistema: {data.get('message', 'N/A')}")
                
        except asyncio.TimeoutError:
            print("⏰ Timeout escuchando mensajes")
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Conexión WebSocket cerrada")
        except Exception as e:
            print(f"❌ Error escuchando mensajes: {e}")
    
    async def send_status_update(self, status: str):
        """Enviar actualización de estado vía WebSocket"""
        if not self.websocket:
            print("❌ WebSocket no está conectado")
            return
            
        message = {
            "type": "update_user_status",
            "status": status,
            "timestamp": time.time()
        }
        
        print(f"📤 Enviando cambio de estado: {status}")
        await self.websocket.send(json.dumps(message))
    
    async def test_websocket_status_integration(self):
        """Probar la integración completa de estados con WebSocket"""
        print("🧪 Probando integración de WebSocket con gestión de estado de usuarios\n")
        
        # 1. Configurar usuario
        if not await self.setup_user():
            return
        
        # 2. Conectar WebSocket
        if not await self.connect_websocket():
            return
        
        # 3. Iniciar listener en background
        listen_task = asyncio.create_task(self.listen_messages())
        
        # 4. Esperar un poco para ver mensajes automáticos
        print("\n⏳ Esperando mensajes automáticos de conexión...")
        await asyncio.sleep(3)
        
        # 5. Probar cambio manual de estado vía WebSocket
        print("\n🔄 Probando cambios manuales de estado...")
        
        test_states = ["banned", "disconnected", "connected", "in_game"]
        for state in test_states:
            await self.send_status_update(state)
            await asyncio.sleep(2)  # Esperar respuesta
        
        # 6. Intentar estado no permitido (debería fallar)
        print("\n🚫 Probando estado no permitido (banned)...")
        await self.send_status_update("banned")
        await asyncio.sleep(2)
        
        print("\n✅ Pruebas de WebSocket completadas")
        
        # 7. Desconectar (debería disparar actualización automática)
        print("\n🔌 Desconectando WebSocket...")
        if self.websocket:
            await self.websocket.close()
        
        # Cancelar listener
        listen_task.cancel()
        
        # 8. Verificar estado final vía API REST
        await self.verify_final_status()
    
    async def verify_final_status(self):
        """Verificar el estado final del usuario vía API REST"""
        print("\n🔍 Verificando estado final vía API REST...")
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            profile_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                final_status = profile_data['user']['status']
                print(f"✅ Estado final del usuario: {final_status}")
            else:
                print(f"❌ Error obteniendo perfil: {profile_response.text}")
                
        except Exception as e:
            print(f"❌ Error verificando estado final: {e}")
    
    async def cleanup(self):
        """Limpiar usuario de prueba"""
        print("\n🧹 Limpiando usuario de prueba...")
        
        try:
            # Credenciales de admin desde .env
            admin_credentials = {
                "username": os.getenv("ADMIN_USERNAME", "admin"),
                "password": os.getenv("ADMIN_PASSWORD", "adminpass123")
            }
            
            # Login como admin
            admin_login_response = requests.post(
                f"{BASE_URL}/login",
                data=admin_credentials
            )
            
            if admin_login_response.status_code == 200:
                admin_token_data = admin_login_response.json()
                admin_token = admin_token_data["access_token"]
                admin_headers = {"Authorization": f"Bearer {admin_token}"}
                
                # Eliminar usuario
                delete_response = requests.delete(
                    f"{BASE_URL}/admin/users/{self.user_id}",
                    headers=admin_headers
                )
                
                if delete_response.status_code == 200:
                    print("✅ Usuario de prueba eliminado exitosamente")
                else:
                    print(f"⚠️  Error eliminando usuario: {delete_response.text}")
            else:
                print(f"⚠️  Error en login de admin: {admin_login_response.text}")
                
        except Exception as e:
            print(f"⚠️  Error durante la limpieza: {e}")

async def main():
    """Función principal"""
    tester = WebSocketTester()
    
    try:
        await tester.test_websocket_status_integration()
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de WebSocket con gestión de estado de usuarios")
    asyncio.run(main())
