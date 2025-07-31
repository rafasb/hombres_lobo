#!/usr/bin/env python3
"""
Script para probar el sistema de votaciones con múltiples jugadores simulados
"""
import asyncio
import websockets  
import json
import requests

# Configuración
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

# Usuarios de prueba
TEST_USERS = [
    {"username": "admin", "password": "adminpass123", "email": "admin@test.com"},
    {"username": "player1", "password": "player1pass", "email": "player1@test.com"},
    {"username": "player2", "password": "player2pass", "email": "player2@test.com"},
    {"username": "player3", "password": "player3pass", "email": "player3@test.com"},
    {"username": "player4", "password": "player4pass", "email": "player4@test.com"},
]

class MultiPlayerVotingTest:
    def __init__(self):
        self.game_id = None
        self.players = []
        
    def create_test_users(self):
        """Crear usuarios de prueba si no existen"""
        print("👥 Creando usuarios de prueba...")
        
        for user_data in TEST_USERS:
            if user_data["username"] == "admin":
                continue  # Admin ya existe
                
            try:
                response = requests.post(f"{BASE_URL}/register", data=user_data)
                if response.status_code == 200:
                    print(f"✅ Usuario {user_data['username']} creado")
                elif response.status_code == 400:
                    print(f"👤 Usuario {user_data['username']} ya existe")
                else:
                    print(f"⚠️ Error creando {user_data['username']}: {response.status_code}")
            except Exception as e:
                print(f"❌ Error creando {user_data['username']}: {e}")
    
    def login_user(self, username, password):
        """Login de un usuario específico"""
        try:
            response = requests.post(f"{BASE_URL}/login", data={"username": username, "password": password})
            if response.status_code == 200:
                token_data = response.json()
                return token_data["access_token"]
            else:
                print(f"❌ Error login {username}: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error login {username}: {e}")
            return None
    
    def create_game(self, admin_token):
        """Crear juego como admin"""
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            game_data = {
                "name": "Multi-Player Voting Test",
                "creator_id": "admin",
                "max_players": 8
            }
            
            response = requests.post(f"{BASE_URL}/games", headers=headers, json=game_data)
            if response.status_code == 200:
                game_info = response.json()
                self.game_id = game_info["id"]
                print(f"✅ Juego creado: {self.game_id}")
                return True
            else:
                print(f"❌ Error creando juego: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error creando juego: {e}")
            return False
    
    async def simulate_player(self, username, password, player_id):
        """Simular un jugador conectándose y participando"""
        token = self.login_user(username, password)
        if not token:
            return
        
        print(f"🔌 {username} conectando...")
        
        try:
            uri = f"{WS_URL}/ws/{self.game_id}?token={token}"
            async with websockets.connect(uri) as websocket:
                print(f"✅ {username} conectado!")
                
                # Unirse al juego
                await websocket.send(json.dumps({"type": "join_game"}))
                
                # Escuchar mensajes y responder
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await self.handle_player_message(websocket, username, data)
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"❌ Error {username}: {e}")
                        break
                        
        except Exception as e:
            print(f"❌ Error conexión {username}: {e}")
    
    async def handle_player_message(self, websocket, username, data):
        """Manejar mensajes para un jugador específico"""
        msg_type = data.get("type", "unknown")
        
        if msg_type == "system_message":
            print(f"💬 {username}: {data.get('message', '')}")
            
        elif msg_type == "game_started":
            print(f"🎮 {username}: Juego iniciado!")
            
        elif msg_type == "phase_changed":
            phase = data.get("phase", "unknown")
            print(f"🔄 {username}: Fase cambiada a {phase}")
            
        elif msg_type == "voting_started":
            vote_type = data.get("vote_type", "unknown")
            targets = data.get("vote_targets", [])
            print(f"🗳️  {username}: Votación iniciada ({vote_type}) - Targets: {len(targets)}")
            
            # Simular voto después de un delay aleatorio
            await asyncio.sleep(3 + hash(username) % 10)  # Delay 3-13 segundos
            
            if targets:
                # Votar por un target aleatorio (basado en hash del username para consistencia)
                target_index = hash(username) % len(targets)
                target = targets[target_index]
                
                vote_message = {"type": "cast_vote", "target_id": target}
                await websocket.send(json.dumps(vote_message))
                print(f"✅ {username}: Voto emitido por {target}")
                
        elif msg_type == "vote_cast":
            voter = data.get("voter_id", "unknown")
            target = data.get("target_id", "unknown")
            if voter != username:  # Solo mostrar votos de otros
                print(f"👀 {username}: {voter} votó por {target}")
                
        elif msg_type == "voting_results":
            results = data.get("results", {})
            eliminated = data.get("eliminated_player")
            print(f"🏆 {username}: Resultados - Eliminado: {eliminated}, Votos: {results}")
            
        elif msg_type == "phase_timer":
            phase = data.get("phase", "unknown")
            time_remaining = data.get("time_remaining", 0)
            if time_remaining % 20 == 0 and time_remaining > 0:  # Mostrar cada 20 segundos
                print(f"⏰ {username}: {phase} - {time_remaining}s")
    
    async def run_test(self):
        """Ejecutar el test completo"""
        print("🧪 Iniciando test multi-jugador del sistema de votaciones...\n")
        
        # 1. Crear usuarios de prueba
        self.create_test_users()
        
        # 2. Login como admin y crear juego
        admin_token = self.login_user("admin", "adminpass123")
        if not admin_token:
            print("❌ No se pudo hacer login como admin")
            return
        
        if not self.create_game(admin_token):
            print("❌ No se pudo crear el juego")
            return
        
        # 3. Simular múltiples jugadores conectándose
        print(f"\n🎮 Iniciando simulación con {len(TEST_USERS)} jugadores...")
        
        # Crear tareas para todos los jugadores
        player_tasks = []
        for i, user_data in enumerate(TEST_USERS):
            task = self.simulate_player(
                user_data["username"], 
                user_data["password"], 
                i
            )
            player_tasks.append(task)
        
        # Esperar un poco antes de iniciar el juego
        await asyncio.sleep(5)
        
        # Iniciar el juego como admin
        print("\n🚀 Iniciando juego como admin...")
        try:
            uri = f"{WS_URL}/ws/{self.game_id}?token={admin_token}"
            async with websockets.connect(uri) as admin_ws:
                await admin_ws.send(json.dumps({"type": "start_game"}))
                print("✅ Comando start_game enviado!")
                
                # Escuchar algunos mensajes como admin
                for _ in range(5):
                    try:
                        message = await asyncio.wait_for(admin_ws.recv(), timeout=2.0)
                        data = json.loads(message)
                        if data.get("type") == "game_started":
                            print("🎊 ¡Juego iniciado exitosamente!")
                            break
                    except asyncio.TimeoutError:
                        continue
                        
        except Exception as e:
            print(f"❌ Error iniciando juego: {e}")
        
        # Ejecutar todos los jugadores en paralelo por tiempo limitado
        try:
            await asyncio.wait_for(
                asyncio.gather(*player_tasks, return_exceptions=True),
                timeout=180  # 3 minutos
            )
        except asyncio.TimeoutError:
            print("\n⏰ Tiempo límite alcanzado - finalizando test")
        
        print("\n✅ Test multi-jugador completado!")

async def main():
    test = MultiPlayerVotingTest()
    await test.run_test()

if __name__ == "__main__":
    asyncio.run(main())
