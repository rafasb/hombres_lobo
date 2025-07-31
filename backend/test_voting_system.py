#!/usr/bin/env python3
"""
Script para probar el sistema de votaciones integrado
"""
import asyncio
import websockets
import json
import requests

# Configuración
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"
USERNAME = "admin"
PASSWORD = "adminpass123"

class VotingTestClient:
    def __init__(self):
        self.token = None
        self.websocket = None
        self.game_id = None
        
    async def login(self):
        """Hacer login y obtener token"""
        print("🔐 Haciendo login...")
        login_data = {"username": USERNAME, "password": PASSWORD}
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        
        if response.status_code != 200:
            raise Exception(f"Error en login: {response.status_code}")
        
        token_data = response.json()
        self.token = token_data["access_token"]
        print("✅ Login exitoso")
        
    async def create_game(self):
        """Crear un juego para pruebas"""
        print("🎮 Creando juego de prueba...")
        headers = {"Authorization": f"Bearer {self.token}"}
        game_data = {
            "name": "Test Voting Game",
            "creator_id": "admin",
            "max_players": 6
        }
        
        response = requests.post(f"{BASE_URL}/games", headers=headers, json=game_data)
        if response.status_code != 200:
            raise Exception(f"Error creando juego: {response.status_code}")
        
        game_info = response.json()
        self.game_id = game_info["id"]
        print(f"✅ Juego creado: {self.game_id}")
        
    async def connect_websocket(self):
        """Conectar WebSocket"""
        print(f"🔌 Conectando WebSocket a juego: {self.game_id}")
        uri = f"{WS_URL}/ws/{self.game_id}?token={self.token}"
        
        self.websocket = await websockets.connect(uri)
        print("✅ WebSocket conectado!")
        
    async def send_message(self, message):
        """Enviar mensaje por WebSocket"""
        if self.websocket:
            await self.websocket.send(json.dumps(message))
        
    async def receive_messages(self, duration=60):
        """Escuchar mensajes por tiempo específico"""
        print(f"👂 Escuchando mensajes por {duration} segundos...")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            while True:
                # Verificar timeout
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > duration:
                    break
                
                # Recibir mensaje con timeout
                try:
                    if self.websocket:
                        message = await asyncio.wait_for(
                            self.websocket.recv(),
                            timeout=2.0
                        )
                        data = json.loads(message)
                        await self.handle_message(data)
                    else:
                        break
                    
                except asyncio.TimeoutError:
                    print(".", end="", flush=True)
                    continue
                    
        except Exception as e:
            print(f"\n❌ Error recibiendo mensajes: {e}")
            
    async def handle_message(self, data):
        """Manejar mensaje recibido"""
        msg_type = data.get("type", "unknown")
        
        if msg_type == "system_message":
            print(f"\n💬 SYSTEM: {data.get('message', '')}")
            
        elif msg_type == "game_started":
            print(f"\n🎮 GAME_STARTED: Juego iniciado con {len(data.get('players', []))} jugadores")
            
        elif msg_type == "phase_changed":
            phase = data.get("phase", "unknown")
            duration = data.get("duration", 0)
            print(f"\n🔄 PHASE_CHANGED: {phase} (duración: {duration}s)")
            
        elif msg_type == "voting_started":
            vote_type = data.get("vote_type", "unknown")
            duration = data.get("duration", 0)
            targets = data.get("vote_targets", [])
            print(f"\n🗳️  VOTING_STARTED: {vote_type} - {duration}s - Targets: {len(targets)}")
            
            # Simular voto automático después de 5 segundos
            await asyncio.sleep(5)
            await self.cast_test_vote(targets)
            
        elif msg_type == "vote_cast":
            voter = data.get("voter_id", "unknown")
            target = data.get("target_id", "unknown")
            print(f"\n✅ VOTE_CAST: {voter} votó por {target}")
            
        elif msg_type == "voting_results":
            results = data.get("results", {})
            eliminated = data.get("eliminated_player")
            is_tie = data.get("is_tie", False)
            print("\n🏆 VOTING_RESULTS:")
            print(f"   Votos: {results}")
            print(f"   Eliminado: {eliminated}")
            print(f"   Empate: {is_tie}")
            
        elif msg_type == "phase_timer":
            phase = data.get("phase", "unknown")
            time_remaining = data.get("time_remaining", 0)
            if time_remaining % 10 == 0:  # Solo mostrar cada 10 segundos
                print(f"\n⏰ TIMER: {phase} - {time_remaining}s restantes")
                
        elif msg_type == "heartbeat":
            print("💓", end="", flush=True)
            
        else:
            print(f"\n📥 {msg_type.upper()}: {json.dumps(data, indent=2)}")
    
    async def cast_test_vote(self, targets):
        """Emitir un voto de prueba"""
        if not targets:
            print("⚠️ No hay targets para votar")
            return
            
        # Votar por el primer target disponible
        target = targets[0]
        vote_message = {
            "type": "cast_vote",
            "target_id": target
        }
        
        print(f"📤 Enviando voto por: {target}")
        await self.send_message(vote_message)
    
    async def test_voting_flow(self):
        """Probar flujo completo de votaciones"""
        try:
            # 1. Login
            await self.login()
            
            # 2. Crear juego
            await self.create_game()
            
            # 3. Conectar WebSocket
            await self.connect_websocket()
            
            # 4. Unirse al juego
            join_message = {"type": "join_game"}
            print("📤 Mensaje join_game enviado")
            await self.send_message(join_message)
            
            await asyncio.sleep(2)
            
            # 5. Iniciar juego (activará el sistema de fases)
            start_message = {"type": "start_game"}
            print("📤 Mensaje start_game enviado - ¡Iniciando sistema de fases!")
            await self.send_message(start_message)
            
            # 6. Escuchar eventos y participar en votación
            await self.receive_messages(duration=300)  # 5 minutos
            
        except Exception as e:
            print(f"❌ Error en test: {e}")
        finally:
            if self.websocket:
                await self.websocket.close()

async def main():
    print("🧪 Iniciando test del sistema de votaciones...")
    
    client = VotingTestClient()
    await client.test_voting_flow()
    
    print("\n✅ Test de votaciones completado!")

if __name__ == "__main__":
    asyncio.run(main())
