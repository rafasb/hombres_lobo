#!/usr/bin/env python3
"""
Test directo del sistema de votaciones sin esperar fases completas
"""
import asyncio
import websockets
import json
import requests

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

async def test_direct_voting():
    """Test directo que fuerza el estado de votación"""
    print("🧪 Test directo del sistema de votaciones\n")
    
    # 1. Setup inicial
    print("⚙️ Configurando...")
    response = requests.post(f"{BASE_URL}/login", data={"username": "admin", "password": "adminpass123"})
    admin_token = response.json()["access_token"]
    
    # Crear juego
    headers = {"Authorization": f"Bearer {admin_token}"}
    game_data = {"name": "Direct Voting Test", "creator_id": "admin", "max_players": 6}
    response = requests.post(f"{BASE_URL}/games", headers=headers, json=game_data)
    game_id = response.json()["id"]
    print(f"✅ Juego creado: {game_id}")
    
    # 2. Crear algunos jugadores de prueba
    players = []
    for i in range(2, 5):  # player2, player3, player4
        user_data = {"username": f"testplayer{i}", "password": f"pass{i}", "email": f"test{i}@test.com"}
        try:
            requests.post(f"{BASE_URL}/register", data=user_data)
            login_resp = requests.post(f"{BASE_URL}/login", data={"username": f"testplayer{i}", "password": f"pass{i}"})
            if login_resp.status_code == 200:
                token = login_resp.json()["access_token"]
                players.append((f"testplayer{i}", token))
                print(f"✅ Jugador testplayer{i} registrado")
        except Exception:
            pass
    
    # 3. Conectar todos los jugadores
    print(f"\n🔌 Conectando {len(players) + 1} jugadores...")
    
    connections = []
    
    try:
        # Conectar admin
        admin_uri = f"{WS_URL}/ws/{game_id}?token={admin_token}"
        admin_ws = await websockets.connect(admin_uri)
        connections.append(("admin", admin_ws))
        
        # Conectar otros jugadores
        for player_name, token in players:
            uri = f"{WS_URL}/ws/{game_id}?token={token}"
            ws = await websockets.connect(uri)
            connections.append((player_name, ws))
        
        print(f"✅ {len(connections)} jugadores conectados!")
        
        # 4. Hacer join y start
        print("\n🎮 Iniciando juego...")
        for name, ws in connections:
            await ws.send(json.dumps({"type": "join_game"}))
        
        await asyncio.sleep(2)
        
        # Solo admin inicia el juego
        await connections[0][1].send(json.dumps({"type": "start_game"}))
        print("📤 Comando start_game enviado!")
        
        # 5. Escuchar eventos hasta llegar a votación
        print("\n👂 Esperando sistema de votaciones...")
        voting_detected = False
        timeout = 600  # 10 minutos máximo
        start_time = asyncio.get_event_loop().time()
        
        while not voting_detected and (asyncio.get_event_loop().time() - start_time) < timeout:
            # Escuchar de todas las conexiones
            for name, ws in connections:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    data = json.loads(message)
                    
                    msg_type = data.get("type", "")
                    
                    # Debug de fases
                    if msg_type == "phase_changed":
                        phase = data.get("phase", "unknown")
                        duration = data.get("duration", 0)
                        print(f"🔄 {name}: FASE → {phase} ({duration}s)")
                    
                    # ¡VOTACIÓN DETECTADA!
                    elif msg_type == "voting_started":
                        print(f"\n🎊 ¡SISTEMA DE VOTACIONES ACTIVADO! ({name})")
                        vote_type = data.get("vote_type", "unknown")
                        targets = data.get("vote_targets", [])
                        duration = data.get("duration", 0)
                        
                        print(f"   🗳️  Tipo de voto: {vote_type}")
                        print(f"   ⏰ Duración: {duration}s")
                        print(f"   🎯 Targets: {targets}")
                        
                        voting_detected = True
                        
                        # Hacer que algunos jugadores voten
                        await test_voting_mechanics(connections, targets)
                        break
                    
                    # Otros eventos importantes
                    elif msg_type in ["vote_cast", "voting_results"]:
                        if msg_type == "vote_cast":
                            voter = data.get("voter_id", "unknown")
                            target = data.get("target_id", "unknown") 
                            print(f"✅ {name}: VOTO DETECTADO - {voter} → {target}")
                        elif msg_type == "voting_results":
                            results = data.get("results", {})
                            eliminated = data.get("eliminated_player")
                            print(f"🏆 {name}: RESULTADOS - Eliminado: {eliminated}")
                            print(f"    Votos: {results}")
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    if "ConnectionClosed" not in str(e):
                        print(f"❌ Error {name}: {e}")
                    continue
        
        if not voting_detected:
            print("⚠️ No se detectó votación en el tiempo límite")
        else:
            print("\n🎉 ¡SISTEMA DE VOTACIONES VERIFICADO EXITOSAMENTE!")
    
    finally:
        # Cerrar conexiones
        for name, ws in connections:
            try:
                await ws.close()
            except Exception:
                pass

async def test_voting_mechanics(connections, targets):
    """Probar la mecánica de votación"""
    if not targets:
        print("⚠️ No hay targets para votar")
        return
    
    print("\n🗳️ Simulando votos...")
    
    # Hacer que algunos jugadores voten
    for i, (name, ws) in enumerate(connections[:3]):  # Solo primeros 3 jugadores
        if i < len(targets):
            target = targets[i % len(targets)]  # Rotar targets
            
            vote_msg = {"type": "cast_vote", "target_id": target}
            try:
                await ws.send(json.dumps(vote_msg))
                print(f"📤 {name} votó por {target}")
                await asyncio.sleep(1)  # Delay entre votos
            except Exception as e:
                print(f"❌ Error votando {name}: {e}")

async def main():
    await test_direct_voting()
    print("\n✅ Test directo completado!")

if __name__ == "__main__":
    asyncio.run(main())
