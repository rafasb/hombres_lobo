#!/usr/bin/env python3
"""
Script de prueba para verificar que los endpoints con modelos de respuesta funcionan correctamente.
Este script prueba los endpoints principales de games y users.
"""

import requests


def test_user_endpoints():
    """Prueba los endpoints de usuarios"""
    base_url = "http://localhost:8000"
    
    print("🧪 Probando endpoints de usuarios...")
    
    # Test 1: Registro de usuario
    print("📝 Test: Registro de usuario")
    register_data = {
        "username": "test_user",
        "email": "test@example.com", 
        "password": "test123"
    }
    
    response = requests.post(f"{base_url}/register", data=register_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Estructura correcta: {bool(data.get('success') and data.get('message') and data.get('user'))}")
        print(f"   Usuario creado: {data.get('user', {}).get('username', 'N/A')}")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # Test 2: Login
    print("🔐 Test: Login de usuario")
    login_data = {
        "username": "test_user",
        "password": "test123"
    }
    
    response = requests.post(f"{base_url}/login", data=login_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Estructura correcta: {bool(data.get('success') and data.get('access_token') and data.get('user_id'))}")
        token = data.get('access_token')
        print(f"   Token obtenido: {token[:20]}...")
        
        # Test 3: Obtener perfil propio
        print("👤 Test: Obtener perfil propio")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/users/me", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Estructura correcta: {bool(data.get('success') and data.get('user'))}")
        else:
            print(f"   ❌ Error: {response.text}")
    else:
        print(f"   ❌ Error: {response.text}")


def test_game_endpoints():
    """Prueba los endpoints de partidas"""
    base_url = "http://localhost:8000"
    
    print("\n🎮 Probando endpoints de partidas...")
    
    # Primero necesitamos obtener un token
    login_data = {"username": "test_user", "password": "test123"}
    response = requests.post(f"{base_url}/login", data=login_data)
    
    if response.status_code != 200:
        print("❌ No se pudo obtener token para pruebas de partidas")
        return
    
    token = response.json().get('access_token')
    user_id = response.json().get('user_id')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Crear partida
    print("🎯 Test: Crear partida")
    game_data = {
        "name": "Partida de Prueba",
        "creator_id": user_id,
        "max_players": 8
    }
    
    response = requests.post(f"{base_url}/games", json=game_data, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Estructura correcta: {bool(data.get('success') and data.get('message') and data.get('game'))}")
        game_id = data.get('game', {}).get('id')
        print(f"   Partida creada: {data.get('game', {}).get('name')} (ID: {game_id})")
        
        # Test 2: Obtener partida
        print("📋 Test: Obtener partida")
        response = requests.get(f"{base_url}/games/{game_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Estructura correcta: {bool(data.get('success') and data.get('game'))}")
        else:
            print(f"   ❌ Error: {response.text}")
        
        # Test 3: Listar partidas
        print("📜 Test: Listar partidas")
        response = requests.get(f"{base_url}/games", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Estructura correcta: {bool(data.get('success') and data.get('games') and 'total_games' in data)}")
            print(f"   Total de partidas: {data.get('total_games', 0)}")
        else:
            print(f"   ❌ Error: {response.text}")
    else:
        print(f"   ❌ Error: {response.text}")


def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de endpoints con modelos de respuesta")
    print("=" * 60)
    
    try:
        test_user_endpoints()
        test_game_endpoints()
        
        print("\n" + "=" * 60)
        print("✅ Pruebas completadas!")
        print("💡 Si ves este mensaje, los endpoints están funcionando correctamente.")
        
    except requests.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor.")
        print("   Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()
