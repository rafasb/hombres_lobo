#!/usr/bin/env python3
"""
Demo completa del cambio manual de fases hasta llegar a votación
"""
import asyncio
import websockets
import json
import requests

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

async def demo_manual_voting():
    """Demo: Llegar a votación usando cambios manuales"""
    print("🎮 DEMO: Cambio manual de fases hasta votación\n")
    
    # Setup
    response = requests.post(f"{BASE_URL}/login", data={"username": "admin", "password": "adminpass123"})
    admin_token = response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    game_data = {"name": "Demo Manual to Voting", "creator_id": "admin", "max_players": 6}
    response = requests.post(f"{BASE_URL}/games", headers=headers, json=game_data)
    game_id = response.json()["id"]
    print(f"✅ Juego creado: {game_id}")
    
    # Conectar
    uri = f"{WS_URL}/ws/{game_id}?token={admin_token}"
    async with websockets.connect(uri) as websocket:
        print("✅ Conectado como creador!")
        
        # Join y start
        await websocket.send(json.dumps({"type": "join_game"}))
        await asyncio.sleep(1)
        await websocket.send(json.dumps({"type": "start_game"}))
        print("📤 Juego iniciado!\n")
        
        # Secuencia de cambios manuales hasta llegar a votación
        voting_reached = False
        
        for i in range(30):  # 30 iteraciones máximo
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(message)
                msg_type = data.get("type", "")
                
                if msg_type == "game_started":
                    print("🎊 Juego iniciado - comenzando secuencia manual...")
                    await asyncio.sleep(2)
                    await force_next_phase(websocket)
                    
                elif msg_type == "success" and data.get("action") == "force_next_phase":
                    old_phase = data.get("data", {}).get("old_phase", "")
                    new_phase = data.get("data", {}).get("new_phase", "")
                    print(f"✅ CAMBIO MANUAL: {old_phase} → {new_phase}")
                    
                    # Si llegamos a voting, ¡éxito!
                    if new_phase == "voting":
                        voting_reached = True
                        print("🎊 ¡VOTACIÓN ALCANZADA CON CAMBIO MANUAL!")
                    else:
                        # Continuar con el siguiente cambio
                        await asyncio.sleep(1)
                        await force_next_phase(websocket)
                
                elif msg_type == "phase_changed":
                    phase = data.get("phase", "")
                    duration = data.get("duration", 0)
                    print(f"🔄 FASE: {phase} (duración: {duration}s)")
                
                elif msg_type == "voting_started":
                    vote_type = data.get("vote_type", "")
                    targets = data.get("vote_targets", [])
                    print("\n🗳️ ¡SISTEMA DE VOTACIÓN ACTIVADO!")
                    print(f"   Tipo: {vote_type}")
                    print(f"   Targets: {targets}")
                    
                    # Probar votar
                    if targets:
                        await asyncio.sleep(2)
                        target = targets[0]
                        vote_msg = {"type": "cast_vote", "target_id": target}
                        await websocket.send(json.dumps(vote_msg))
                        print(f"📤 Voto emitido por: {target}")
                
                elif msg_type == "vote_cast":
                    voter = data.get("voter_id", "")
                    target = data.get("target_id", "")
                    print(f"✅ VOTO CONFIRMADO: {voter} → {target}")
                
                elif msg_type == "voting_results":
                    results = data.get("results", {})
                    eliminated = data.get("eliminated_player")
                    print("🏆 RESULTADOS DE VOTACIÓN:")
                    print(f"   Votos: {results}")
                    print(f"   Eliminado: {eliminated}")
                    print("\n🎉 ¡DEMO COMPLETADA EXITOSAMENTE!")
                    break
                
                elif msg_type == "error":
                    error_code = data.get("error_code", "")
                    message_text = data.get("message", "")
                    print(f"❌ ERROR: {error_code} - {message_text}")
                
                if voting_reached and msg_type == "voting_started":
                    break
                    
            except asyncio.TimeoutError:
                print(".", end="", flush=True)
                continue
            except Exception as e:
                print(f"\n❌ Error: {e}")
                break
        
        if not voting_reached:
            print("\n⚠️ No se alcanzó la fase de votación")
        else:
            print("\n🎊 ¡ÉXITO! Se alcanzó la votación usando cambios manuales")

async def force_next_phase(websocket):
    """Enviar comando de cambio de fase"""
    force_msg = {"type": "force_next_phase"}
    await websocket.send(json.dumps(force_msg))
    print("📤 Comando force_next_phase enviado")

async def main():
    await demo_manual_voting()
    print("\n✅ Demo del cambio manual completada!")

if __name__ == "__main__":
    asyncio.run(main())
