#!/usr/bin/env python3
"""
Script de prueba para demostrar el nuevo endpoint de actualización de estado de usuario.
"""

import requests
import os
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
BASE_URL = "http://localhost:8000"

# Crear un nombre único para evitar conflictos
unique_suffix = str(int(time.time()))
TEST_USER = {
    "username": f"test_status_user_{unique_suffix}",
    "email": f"test_status_{unique_suffix}@example.com",
    "password": "testpassword123"
}

# Credenciales de admin desde .env
ADMIN_CREDENTIALS = {
    "username": os.getenv("ADMIN_USERNAME", "admin"),
    "password": os.getenv("ADMIN_PASSWORD", "adminpass123")
}

def test_user_status_endpoint():
    print("🧪 Probando el nuevo endpoint de actualización de estado de usuario\n")
    
    user_id = None
    access_token = None
    admin_token = None
    
    try:
        # 1. Registrar un usuario de prueba
        print("1. Registrando usuario de prueba...")
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
            user_id = user_data["user"]["id"]  # El ID está en user_data["user"]["id"]
        else:
            print(f"❌ Error al registrar usuario: {register_response.text}")
            return
        
        # 2. Login para obtener token
        print("\n2. Haciendo login...")
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
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
        else:
            print(f"❌ Error en login: {login_response.text}")
            return
        
        # 3. Probar cambio de estado propio (connected)
        print("\n3. Cambiando estado propio a 'connected'...")
        status_update_response = requests.put(
            f"{BASE_URL}/users/{user_id}/status",
            json={"status": "connected"},
            headers=headers
        )
        
        if status_update_response.status_code == 200:
            print("✅ Estado actualizado exitosamente")
            response_data = status_update_response.json()
            print(f"   - Estado anterior: {response_data['old_status']}")
            print(f"   - Estado nuevo: {response_data['new_status']}")
            print(f"   - Actualizado en: {response_data['updated_at']}")
        else:
            print(f"❌ Error al actualizar estado: {status_update_response.text}")
        
        # 4. Probar cambio de estado a 'disconnected'
        print("\n4. Cambiando estado a 'disconnected'...")
        status_update_response = requests.put(
            f"{BASE_URL}/users/{user_id}/status",
            json={"status": "disconnected"},
            headers=headers
        )
        
        if status_update_response.status_code == 200:
            print("✅ Estado actualizado exitosamente")
            response_data = status_update_response.json()
            print(f"   - Estado anterior: {response_data['old_status']}")
            print(f"   - Estado nuevo: {response_data['new_status']}")
        else:
            print(f"❌ Error al actualizar estado: {status_update_response.text}")
        
        # 5. Probar intentar banear usuario (debería fallar si no es admin)
        print("\n5. Intentando banear usuario (debería fallar para no-admin)...")
        ban_response = requests.put(
            f"{BASE_URL}/users/{user_id}/status",
            json={"status": "banned"},
            headers=headers
        )
        
        if ban_response.status_code == 403:
            print("✅ Correcto: No-admin no puede banear usuarios")
        else:
            print(f"⚠️  Inesperado: {ban_response.status_code} - {ban_response.text}")
        
        # 6. Verificar el perfil actualizado
        print("\n6. Verificando perfil actualizado...")
        profile_response = requests.get(
            f"{BASE_URL}/users/me",
            headers=headers
        )
        
        if profile_response.status_code == 200:
            print("✅ Perfil obtenido exitosamente")
            profile_data = profile_response.json()
            print(f"   - Estado actual: {profile_data['user']['status']}")
            print(f"   - Última actualización: {profile_data['user']['updated_at']}")
        else:
            print(f"❌ Error al obtener perfil: {profile_response.text}")
        
        print("\n🎉 Prueba completada!")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
    
    finally:
        # 7. Limpiar: Eliminar el usuario de prueba usando credenciales de admin
        if user_id:
            print("\n7. Limpiando: Eliminando usuario de prueba...")
            try:
                # Login como admin
                admin_login_response = requests.post(
                    f"{BASE_URL}/login",
                    data={
                        "username": ADMIN_CREDENTIALS["username"],
                        "password": ADMIN_CREDENTIALS["password"]
                    }
                )
                
                if admin_login_response.status_code == 200:
                    admin_token_data = admin_login_response.json()
                    admin_token = admin_token_data["access_token"]
                    admin_headers = {"Authorization": f"Bearer {admin_token}"}
                    
                    # Eliminar el usuario de prueba
                    delete_response = requests.delete(
                        f"{BASE_URL}/admin/users/{user_id}",
                        headers=admin_headers
                    )
                    
                    if delete_response.status_code == 200:
                        print("✅ Usuario de prueba eliminado exitosamente")
                    else:
                        print(f"⚠️  Error al eliminar usuario: {delete_response.text}")
                else:
                    print(f"⚠️  Error en login de admin: {admin_login_response.text}")
                    
            except Exception as cleanup_error:
                print(f"⚠️  Error durante la limpieza: {cleanup_error}")


if __name__ == "__main__":
    try:
        test_user_status_endpoint()
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está el servidor ejecutándose en http://localhost:8000?")
        print("   Ejecuta: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
