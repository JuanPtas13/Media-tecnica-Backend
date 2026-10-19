#!/usr/bin/env python3
"""
Test simple para crear usuario y testear validación de contraseña
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("\n" + "=" * 80)
print("TEST: Crear Usuario - Validación de Contraseña 72 bytes")
print("=" * 80)

# Test 1: Contraseña válida (corta)
print("\n[TEST 1] Contraseña VÁLIDA (corta - 10 bytes)")
print("-" * 80)

data1 = {
    "nombre": "Test",
    "apellido1": "User",
    "correo": f"test1-{int(time.time())}@example.com",
    "contrasena": "MyPass123!",
    "rol_id": 1
}

print(f"Email: {data1['correo']}")
print(f"Contraseña: {data1['contrasena']}")
print(f"Caracteres: {len(data1['contrasena'])}")
print(f"Bytes UTF-8: {len(data1['contrasena'].encode('utf-8'))}")
print(f"\nEnviando POST /usuarios/...")

try:
    response = requests.post(f"{BASE_URL}/usuarios/", json=data1, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)[:500]}")
    
    if response.status_code == 201:
        print("✅ ÉXITO - Usuario creado")
    else:
        print("❌ ERROR - No se creó el usuario")
except Exception as e:
    print(f"❌ ERROR de conexión: {str(e)}")

# Test 2: Contraseña válida (más larga, con acentos)
print("\n\n[TEST 2] Contraseña VÁLIDA (con acentos - 13 caracteres/15 bytes)")
print("-" * 80)

data2 = {
    "nombre": "Test",
    "apellido1": "User",
    "correo": f"test2-{int(time.time())}@example.com",
    "contrasena": "Contraseña123",
    "rol_id": 1
}

print(f"Email: {data2['correo']}")
print(f"Contraseña: {data2['contrasena']}")
print(f"Caracteres: {len(data2['contrasena'])}")
print(f"Bytes UTF-8: {len(data2['contrasena'].encode('utf-8'))}")
print(f"\nEnviando POST /usuarios/...")

try:
    response = requests.post(f"{BASE_URL}/usuarios/", json=data2, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)[:500]}")
    
    if response.status_code == 201:
        print("✅ ÉXITO - Usuario creado")
    else:
        print("❌ ERROR - No se creó el usuario")
except Exception as e:
    print(f"❌ ERROR de conexión: {str(e)}")

# Test 3: Contraseña INVÁLIDA (Unicode larga - excede 72 bytes)
print("\n\n[TEST 3] Contraseña INVÁLIDA (Unicode larga - 40 caracteres/120 bytes)")
print("-" * 80)

data3 = {
    "nombre": "Test",
    "apellido1": "User",
    "correo": f"test3-{int(time.time())}@example.com",
    "contrasena": "中文密码中文密码中文密码中文密码中文密码中文密码中文密码",
    "rol_id": 1
}

print(f"Email: {data3['correo']}")
print(f"Contraseña: {data3['contrasena']}")
print(f"Caracteres: {len(data3['contrasena'])}")
print(f"Bytes UTF-8: {len(data3['contrasena'].encode('utf-8'))}")
print(f"\nEnviando POST /usuarios/...")

try:
    response = requests.post(f"{BASE_URL}/usuarios/", json=data3, timeout=10)
    print(f"Status Code: {response.status_code}")
    resp_json = response.json()
    print(f"Response: {json.dumps(resp_json, indent=2)[:500]}")
    
    if response.status_code == 422:
        print("✅ CORRECTO - Rechazada como debe ser")
    else:
        print(f"❌ ERROR - Debería ser 422, pero es {response.status_code}")
except Exception as e:
    print(f"❌ ERROR de conexión: {str(e)}")

# Test 4: Login
print("\n\n[TEST 4] Login con Contraseña Válida")
print("-" * 80)

login_data = {
    "email": data1['correo'],
    "contraseña": "MyPass123!"
}

print(f"Email: {login_data['email']}")
print(f"Contraseña: {login_data['contraseña']}")
print(f"Bytes UTF-8: {len(login_data['contraseña'].encode('utf-8'))}")
print(f"\nEnviando POST /auth/login...")

try:
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        resp = response.json()
        if 'access_token' in str(resp):
            print("✅ ÉXITO - Token recibido")
        else:
            print(f"Response: {json.dumps(resp, indent=2)[:500]}")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)[:500]}")
        print("❌ ERROR - No hizo login")
except Exception as e:
    print(f"❌ ERROR de conexión: {str(e)}")

print("\n" + "=" * 80)
print("FIN DE TESTS")
print("=" * 80 + "\n")
