#!/usr/bin/env python3
"""
Test del sistema de cambio manual de fases
"""
import asyncio
import websockets
import json
import requests

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

async def test_manual_phase_change():
    """Test del cambio manual de fases"""
    print("🧪 Test del cambio manual de fases\n")
    
    # 1. Setup inicial
    print("⚙️ Configurando...")
    response = requests.post(f"{BASE_URL}/login", data={"username": "admin", "password": "adminpass123"})
    admin_token = response.json()["access_token"]
    
    # Crear juego
    headers = {"Authorization": f"Bearer {admin_token}"}
    game_data = {"name": "Manual Phase Test", "creator_id": "admin", "max_players": 6}
    response = requests.post(f"{BASE_URL}/games", headers=headers, json=game_data)
    game_id = response.json()["id"]
    print(f"✅ Juego creado: {game_id}")
    
    # 2. Conectar como admin (creador)
    print("\n🔌 Conectando como creador...")
    uri = f"{WS_URL}/ws/{game_id}?token={admin_token}"
    
    async with websockets.connect(uri) as websocket:
        print("✅ Conectado como creador!")
        
        # 3. Unirse y iniciar juego
        await websocket.send(json.dumps({"type": "join_game"}))
        await asyncio.sleep(1)
        await websocket.send(json.dumps({"type": "start_game"}))
        print("📤 Juego iniciado!")
        
        # 4. Escuchar eventos y probar cambios manuales
        await test_manual_controls(websocket)

async def test_manual_controls(websocket):
    """Probar controles manuales de fase"""
    print("\n🎮 Iniciando test de controles manuales...")
    
    phase_changes = 0
    max_changes = 5  # Probar 5 cambios de fase
    
    # Esperar a que el juego se inicie y luego hacer cambios manuales
    for i in range(60):  # 60 segundos máximo
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
            data = json.loads(message)
            msg_type = data.get("type", "")
            
            # Detectar cuando el juego está en curso
            if msg_type == "phase_changed":
                phase = data.get("phase", "unknown")
                duration = data.get("duration", 0)
                print(f"🔄 FASE AUTOMÁTICA: {phase} ({duration}s)")
                
                # Después de la primera fase automática, empezar cambios manuales
                if phase_changes < max_changes:
                    await asyncio.sleep(3)  # Esperar 3 segundos
                    print(f"\n📤 FORZANDO CAMBIO DE FASE {phase_changes + 1}/{max_changes}...")
                    
                    # Enviar comando de cambio manual
                    force_message = {"type": "force_next_phase"}
                    await websocket.send(json.dumps(force_message))
                    phase_changes += 1
            
            elif msg_type == "success" and data.get("action") == "force_next_phase":
                old_phase = data.get("data", {}).get("old_phase", "unknown")
                new_phase = data.get("data", {}).get("new_phase", "unknown")
                print(f"✅ CAMBIO MANUAL EXITOSO: {old_phase} → {new_phase}")
            
            elif msg_type == "voting_started":
                vote_type = data.get("vote_type", "unknown")
                targets = data.get("vote_targets", [])
                print(f"🗳️ VOTACIÓN ACTIVADA: {vote_type} - {len(targets)} targets")
                print("🎊 ¡Sistema de votaciones funcionando con cambio manual!")
                
                # Probar votar durante la votación forzada
                if targets:
                    await asyncio.sleep(2)
                    target = targets[0]
                    vote_msg = {"type": "cast_vote", "target_id": target}
                    await websocket.send(json.dumps(vote_msg))
                    print(f"📤 Voto emitido por {target}")
            
            elif msg_type == "vote_cast":
                voter = data.get("voter_id", "unknown")
                target = data.get("target_id", "unknown")
                print(f"✅ VOTO CONFIRMADO: {voter} → {target}")
            
            elif msg_type == "voting_results":
                results = data.get("results", {})
                eliminated = data.get("eliminated_player")
                print(f"🏆 RESULTADOS: Eliminado: {eliminated}, Votos: {results}")
            
            elif msg_type == "error":
                error_code = data.get("error_code", "UNKNOWN")
                message = data.get("message", "Error desconocido")
                print(f"❌ ERROR: {error_code} - {message}")
            
            elif msg_type == "system_message":
                message_text = data.get("message", "")
                if "started" in message_text.lower() or "phase" in message_text.lower():
                    print(f"💬 SISTEMA: {message_text}")
            
            # Salir si hemos hecho suficientes cambios
            if phase_changes >= max_changes:
                print(f"\n🎉 ¡Test completado! Se realizaron {phase_changes} cambios manuales de fase")
                break
                
        except asyncio.TimeoutError:
            print(".", end="", flush=True)
            continue
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break
    
    if phase_changes < max_changes:
        print(f"\n⚠️ Test terminado antes de completar todos los cambios ({phase_changes}/{max_changes})")

async def main():
    try:
        await test_manual_phase_change()
        print("\n✅ Test de cambio manual de fases completado!")
    except Exception as e:
        print(f"\n❌ Error en test: {e}")

if __name__ == "__main__":
    asyncio.run(main())
