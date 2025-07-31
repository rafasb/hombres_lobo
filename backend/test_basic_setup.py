#!/usr/bin/env python3
"""
Script simple para verificar que el servidor funciona y probar votaciones
"""
import requests

BASE_URL = "http://localhost:8000"

def test_server():
    """Verificar que el servidor está funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Servidor funcionando - OpenAPI docs disponibles")
            return True
        else:
            print(f"⚠️ Servidor responde pero con status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Servidor no disponible: {e}")
        return False

def test_login():
    """Probar login de admin"""
    try:
        login_data = {"username": "admin", "password": "adminpass123"}
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login exitoso")
            return token_data["access_token"]
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def test_create_game(token):
    """Crear un juego de prueba"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        game_data = {
            "name": "Test Voting Game",
            "creator_id": "admin",
            "max_players": 6
        }
        
        response = requests.post(
            f"{BASE_URL}/games", 
            headers=headers,
            json=game_data
        )
        
        if response.status_code == 200:
            game_info = response.json()
            print(f"✅ Juego creado: {game_info['id']}")
            return game_info['id']
        else:
            print(f"❌ Error creando juego: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creando juego: {e}")
        return None

def main():
    print("🧪 Verificando configuración del sistema de votaciones...\n")
    
    # 1. Verificar servidor
    if not test_server():
        print("\n❌ El servidor no está funcionando. Ejecuta:")
        print("   cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # 2. Probar login
    token = test_login()
    if not token:
        print("\n❌ No se pudo hacer login. Verifica que existe el usuario admin.")
        return
    
    # 3. Crear juego de prueba
    game_id = test_create_game(token)
    if game_id:
        print("\n✅ Sistema básico funcionando correctamente!")
        print("\n📋 Próximos pasos:")
        print("   1. Ejecutar: python test_voting_system.py (para prueba completa)")
        print("   2. Abrir WebSocket en navegador o usar herramienta como wscat")
        print(f"   3. Conectar a: ws://localhost:8000/ws/{game_id}?token=<tu_token>")
    else:
        print("\n❌ Error en configuración del juego")
    
    print(f"\n🔑 Token para pruebas: {token[:50]}...")

if __name__ == "__main__":
    main()
