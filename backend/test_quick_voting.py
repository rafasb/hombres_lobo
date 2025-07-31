#!/usr/bin/env python3
"""
Test rápido del sistema de votaciones con fases aceleradas
"""
import asyncio
import websockets
import json
import requests

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

class QuickVotingTest:
    def __init__(self):
        self.game_id = None
        
    async def create_game_and_players(self):
        """Crear juego y registrar jugadores"""
        print("🎮 Configurando test rápido...")
        
        # Login admin
        response = requests.post(f"{BASE_URL}/login", data={"username": "admin", "password": "adminpass123"})
        admin_token = response.json()["access_token"]
        
        # Crear juego
        headers = {"Authorization": f"Bearer {admin_token}"}
        game_data = {"name": "Quick Test", "creator_id": "admin", "max_players": 4}
        response = requests.post(f"{BASE_URL}/games", headers=headers, json=game_data)
        self.game_id = response.json()["id"]
        print(f"✅ Juego creado: {self.game_id}")
        
        return admin_token
    
    async def simulate_quick_test(self):
        """Test rápido con debug de fases"""
        admin_token = await self.create_game_and_players()
        
        print("🔌 Conectando como admin...")
        uri = f"{WS_URL}/ws/{self.game_id}?token={admin_token}"
        
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado!")
            
            # Unirse y iniciar juego
            await websocket.send(json.dumps({"type": "join_game"}))
            await asyncio.sleep(1)
            await websocket.send(json.dumps({"type": "start_game"}))
            print("📤 Juego iniciado!")
            
            # Escuchar por tiempo limitado
            timeout = 300  # 5 minutos
            start_time = asyncio.get_event_loop().time()
            
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > timeout:
                    print("⏰ Timeout alcanzado")
                    break
                
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    await self.handle_message(data)
                    
                except asyncio.TimeoutError:
                    print(".", end="", flush=True)
                    continue
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    break
    
    async def handle_message(self, data):
        """Manejar mensajes recibidos"""
        msg_type = data.get("type", "unknown")
        
        if msg_type == "phase_changed":
            phase = data.get("phase", "unknown")
            duration = data.get("duration", 0)
            print(f"\n🔄 FASE: {phase} ({duration}s)")
            
        elif msg_type == "voting_started":
            vote_type = data.get("vote_type", "unknown")
            targets = data.get("vote_targets", [])
            duration = data.get("duration", 0)
            print("\n🗳️ VOTACIÓN INICIADA!")
            print(f"   Tipo: {vote_type}")
            print(f"   Duración: {duration}s")
            print(f"   Targets: {targets}")
            print("   🎊 ¡SISTEMA DE VOTACIONES FUNCIONANDO!")
            
        elif msg_type == "vote_cast":
            voter = data.get("voter_id", "unknown")
            target = data.get("target_id", "unknown")
            print(f"\n✅ VOTO: {voter} → {target}")
            
        elif msg_type == "voting_results":
            results = data.get("results", {})
            eliminated = data.get("eliminated_player")
            print("\n🏆 RESULTADOS:")
            print(f"   Votos: {results}")
            print(f"   Eliminado: {eliminated}")
            
        elif msg_type == "phase_timer":
            phase = data.get("phase", "unknown")
            remaining = data.get("time_remaining", 0)
            if remaining % 30 == 0 and remaining > 0:  # Cada 30 segundos
                print(f"\n⏰ {phase.upper()}: {remaining}s restantes")
                
        elif msg_type == "system_message":
            message = data.get("message", "")
            if "started" in message.lower() or "phase" in message.lower():
                print(f"\n💬 {message}")
        
        else:
            # Otros mensajes importantes
            if msg_type in ["game_started", "heartbeat"]:
                return
            print(f"\n📥 {msg_type}: {data}")

async def main():
    print("🧪 Test rápido del sistema de votaciones")
    print("📋 Objetivo: Verificar que llegamos a la fase de votación\n")
    
    test = QuickVotingTest()
    await test.simulate_quick_test()
    
    print("\n✅ Test completado!")

if __name__ == "__main__":
    asyncio.run(main())
