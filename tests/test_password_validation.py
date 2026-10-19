#!/usr/bin/env python3
"""
Script de Testing: Validación de Contraseñas
Verifica que la solución del problema "password cannot be longer than 72 bytes" funciona correctamente.

Uso:
    python test_password_validation.py
"""

import requests
import json
from typing import Dict, Any

# Configuración
BASE_URL = "http://localhost:8000"
USUARIO_BASE = {
    "nombre": "Test",
    "apellido1": "Usuario",
    "correo": f"test{int(__import__('time').time())}@example.com",
    "rol_id": 1
}

# Colores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_test(name: str, passed: bool, response: Dict[str, Any] = None):
    """Imprime resultado de test"""
    status = f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}" if passed else f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
    print(f"{status} - {name}")
    
    if response and not passed:
        print(f"    Respuesta: {json.dumps(response, indent=2)[:200]}...")


def test_contrasena_valida():
    """Test 1: Contraseña válida"""
    print(f"\n{Colors.HEADER}Test 1: Contraseña Válida (8-20 caracteres ASCII){Colors.ENDC}")
    
    data = USUARIO_BASE.copy()
    data["contrasena"] = "ValidPass123!"
    
    try:
        response = requests.post(f"{BASE_URL}/usuarios/", json=data)
        passed = response.status_code == 201
        print_test("Crear usuario con contraseña válida", passed, response.json() if not passed else None)
        
        if passed:
            print(f"    Email: {data['correo']}")
            print(f"    Contraseña: {data['contrasena']} ({len(data['contrasena'].encode('utf-8'))} bytes UTF-8)")
        
        return response.json() if passed else None
    except Exception as e:
        print_test("Crear usuario con contraseña válida", False)
        print(f"    Error: {str(e)}")
        return None


def test_contrasena_corta():
    """Test 2: Contraseña demasiado corta"""
    print(f"\n{Colors.HEADER}Test 2: Contraseña Demasiado Corta (< 8 caracteres){Colors.ENDC}")
    
    data = USUARIO_BASE.copy()
    data["correo"] = f"test{int(__import__('time').time())}@example.com"
    data["contrasena"] = "short"
    
    try:
        response = requests.post(f"{BASE_URL}/usuarios/", json=data)
        passed = response.status_code == 422
        print_test("Rechazar contraseña corta", passed, response.json() if passed else None)
        
        if passed:
            print(f"    Contraseña: '{data['contrasena']}' ({len(data['contrasena'])} caracteres)")
            detail = response.json().get("detail", [])
            if isinstance(detail, list) and detail:
                print(f"    Error: {detail[0].get('msg', 'Unknown error')}")
    except Exception as e:
        print_test("Rechazar contraseña corta", False)
        print(f"    Error: {str(e)}")


def test_contrasena_unicode_larga():
    """Test 3: Contraseña con caracteres Unicode que excede 72 bytes"""
    print(f"\n{Colors.HEADER}Test 3: Contraseña Unicode Larga (> 72 bytes UTF-8){Colors.ENDC}")
    
    data = USUARIO_BASE.copy()
    data["correo"] = f"test{int(__import__('time').time())}@example.com"
    # Caracteres chinos = 3 bytes cada uno en UTF-8
    # 25 caracteres * 3 = 75 bytes (excede 72)
    data["contrasena"] = "中文密码1234567890中文密码123456"  # 25 caracteres = 75 bytes
    
    try:
        response = requests.post(f"{BASE_URL}/usuarios/", json=data)
        passed = response.status_code == 422
        print_test("Rechazar contraseña Unicode larga", passed, response.json() if passed else None)
        
        if passed:
            bytes_count = len(data["contrasena"].encode('utf-8'))
            print(f"    Contraseña: '{data['contrasena']}'")
            print(f"    Caracteres: {len(data['contrasena'])}, Bytes UTF-8: {bytes_count}")
            detail = response.json().get("detail", [])
            if isinstance(detail, list) and detail:
                print(f"    Error: {detail[0].get('msg', 'Unknown error')}")
    except Exception as e:
        print_test("Rechazar contraseña Unicode larga", False)
        print(f"    Error: {str(e)}")


def test_contrasena_unicode_valida():
    """Test 4: Contraseña con caracteres Unicode pero dentro del límite"""
    print(f"\n{Colors.HEADER}Test 4: Contraseña Unicode Válida (< 72 bytes){Colors.ENDC}")
    
    data = USUARIO_BASE.copy()
    data["correo"] = f"test{int(__import__('time').time())}@example.com"
    # Caracteres chinos = 3 bytes cada uno
    # 20 caracteres * 3 = 60 bytes (dentro del límite)
    data["contrasena"] = "中文密码1234567890中文1"  # 20 caracteres = 60 bytes
    
    try:
        response = requests.post(f"{BASE_URL}/usuarios/", json=data)
        passed = response.status_code == 201
        print_test("Crear usuario con contraseña Unicode válida", passed, response.json() if not passed else None)
        
        if passed:
            bytes_count = len(data["contrasena"].encode('utf-8'))
            print(f"    Contraseña: '{data['contrasena']}'")
            print(f"    Caracteres: {len(data['contrasena'])}, Bytes UTF-8: {bytes_count}")
    except Exception as e:
        print_test("Crear usuario con contraseña Unicode válida", False)
        print(f"    Error: {str(e)}")


def test_login_valido(usuario: Dict[str, Any]):
    """Test 5: Login con contraseña válida"""
    if not usuario:
        print(f"\n{Colors.WARNING}Test 5: SKIP - No hay usuario válido del test anterior{Colors.ENDC}")
        return
    
    print(f"\n{Colors.HEADER}Test 5: Login con Contraseña Válida{Colors.ENDC}")
    
    data = {
        "email": usuario["data"]["correo"],
        "contraseña": "ValidPass123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        passed = response.status_code == 200 and "access_token" in response.json()
        print_test("Login exitoso", passed, response.json() if not passed else None)
        
        if passed:
            print(f"    Email: {data['email']}")
            token = response.json().get("access_token", "")
            print(f"    Token: {token[:20]}...")
    except Exception as e:
        print_test("Login exitoso", False)
        print(f"    Error: {str(e)}")


def test_login_contrasena_larga():
    """Test 6: Login rechaza contraseña demasiado larga"""
    print(f"\n{Colors.HEADER}Test 6: Login Rechaza Contraseña Larga (> 72 bytes){Colors.ENDC}")
    
    data = {
        "email": "test@example.com",
        "contraseña": "中文密码1234567890中文密码123456"  # 75 bytes
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        passed = response.status_code == 422
        print_test("Rechazar login con contraseña larga", passed, response.json() if passed else None)
        
        if passed:
            bytes_count = len(data["contraseña"].encode('utf-8'))
            print(f"    Contraseña bytes: {bytes_count} (límite: 72)")
            detail = response.json().get("detail", [])
            if isinstance(detail, list) and detail:
                print(f"    Error: {detail[0].get('msg', 'Unknown error')}")
    except Exception as e:
        print_test("Rechazar login con contraseña larga", False)
        print(f"    Error: {str(e)}")


def test_bytes_utils():
    """Test 7: Utilidades para entender bytes UTF-8"""
    print(f"\n{Colors.HEADER}Test 7: Referencia - Bytes UTF-8 para Diferentes Caracteres{Colors.ENDC}")
    
    ejemplos = [
        ("password123", "ASCII simple"),
        ("contraseña123", "Con ñ (acentos)"),
        ("密码123", "Chino (3 bytes por carácter)"),
        ("🔐pass🔐", "Con emojis (4 bytes por emoji)"),
        ("中文密码中文密码中文密码中文密码", "16 caracteres chinos"),
    ]
    
    for text, desc in ejemplos:
        chars = len(text)
        bytes_count = len(text.encode('utf-8'))
        valid = bytes_count <= 72
        status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if valid else f"{Colors.FAIL}✗{Colors.ENDC}"
        print(f"  {status} '{text}' - {chars} chars, {bytes_count} bytes - {desc}")


def main():
    """Ejecutar todos los tests"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}=" * 60)
    print("TESTING: Validación de Contraseñas - Error 72 bytes")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}{Colors.ENDC}\n")
    
    # Verificar que el backend esté disponible
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=2)
        if response.status_code != 200:
            raise Exception("Backend no responde correctamente")
    except Exception as e:
        print(f"{Colors.FAIL}❌ ERROR: No se puede conectar a {BASE_URL}{Colors.ENDC}")
        print(f"   Asegúrate que FastAPI está corriendo: python -m uvicorn app.main:app --reload")
        return
    
    # Tests
    usuario1 = test_contrasena_valida()
    test_contrasena_corta()
    test_contrasena_unicode_larga()
    test_contrasena_unicode_valida()
    test_login_valido(usuario1)
    test_login_contrasena_larga()
    test_bytes_utils()
    
    # Resumen
    print(f"\n{Colors.BOLD}{Colors.HEADER}=" * 60)
    print("TESTING COMPLETADO")
    print("=" * 60)
    print(f"Revisa los resultados arriba.")
    print(f"Todos los tests deben mostrar ✓ PASS (excepto los que intencionalmente fallan).")
    print(f"Ver: {Colors.OKBLUE}README_COMPLEMENTARIO.md{Colors.ENDC} para más detalles.")
    print(f"{Colors.ENDC}\n")


if __name__ == "__main__":
    main()
