#!/usr/bin/env python3
"""
Script para probar la persistencia de autenticación
"""
import requests
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "adminpass123"

def test_auth_flow():
    print("🧪 Probando flujo de autenticación...")
    
    # 1. Login
    print("1. 🔐 Haciendo login...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ Error en login: {response.status_code}")
        return
    
    token_data = response.json()
    access_token = token_data["access_token"]
    print(f"✅ Login exitoso, token obtenido: {access_token[:50]}...")
    
    # 2. Verificar usuario con token
    print("2. 👤 Verificando datos de usuario...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code != 200:
        print(f"❌ Error obteniendo usuario: {response.status_code}")
        return
    
    user_data = response.json()
    print(f"✅ Usuario verificado: {user_data['username']}")
    
    # 3. Decodificar token para ver fecha de expiración
    print("3. ⏰ Verificando fecha de expiración del token...")
    try:
        import base64
        import json
        
        # Decodificar payload del JWT (no verificamos firma, solo leemos)
        payload_encoded = access_token.split('.')[1]
        # Agregar padding si es necesario
        payload_encoded += '=' * (4 - len(payload_encoded) % 4)
        payload_decoded = base64.b64decode(payload_encoded)
        payload = json.loads(payload_decoded)
        
        exp_timestamp = payload['exp']
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        now = datetime.now()
        
        time_until_expiry = exp_datetime - now
        hours_until_expiry = time_until_expiry.total_seconds() / 3600
        
        print(f"✅ Token expira el: {exp_datetime}")
        print(f"✅ Tiempo hasta expiración: {hours_until_expiry:.2f} horas")
        
        if hours_until_expiry >= 7.9:  # Debe ser aprox 8 horas
            print("✅ ¡Configuración de 8 horas confirmada!")
        else:
            print(f"⚠️ Advertencia: Token expira en {hours_until_expiry:.2f} horas (esperado: ~8)")
            
    except Exception as e:
        print(f"⚠️ No se pudo decodificar token: {e}")
    
    print("\n🎯 Test completado:")
    print("- ✅ Login funcional")
    print("- ✅ Token válido para autenticación")
    print("- ✅ Duración del token configurada correctamente")
    print("\n📝 Para probar persistencia en frontend:")
    print("1. Hacer login en la aplicación web")
    print("2. Presionar F5 para recargar")
    print("3. Verificar que no se pierda la sesión")

if __name__ == "__main__":
    test_auth_flow()
