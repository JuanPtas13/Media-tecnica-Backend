# 🔐 GUÍA DE PRUEBAS Y LOGS DE AUTENTICACIÓN - FASTAPI JWT

Complete guide for testing, logging, and error detection in JWT authentication system.

---

## 📋 CONTENIDO NUEVO

### ✅ 1. Archivo de Tests: `tests/test_auth_roles.py`

Tests completos con `pytest` y `TestClient` de FastAPI.

**Clases de tests incluidas:**

| Clase | Descripción |
|-------|------------|
| `TestLogin` | Login exitoso, errores de credenciales |
| `TestAuthentication` | Validación de tokens, expiración |
| `TestRolesAndAuthorization` | Control de acceso por roles |
| `TestCommonErrors` | Detección de errores comunes |
| `TestFlowComplete` | Flujos end-to-end (login → acceso) |
| `TestEdgeCases` | Casos raros y edge cases |

**Cómo ejecutar:**

```bash
# Instalar pytest
pip install pytest pytest-asyncio

# Ejecutar todos los tests
pytest tests/test_auth_roles.py -v

# Ejecutar solo TestLogin
pytest tests/test_auth_roles.py::TestLogin -v

# Ejecutar un test específico
pytest tests/test_auth_roles.py::TestLogin::test_login_exitoso -v

# Ejecutar con salida de print
pytest tests/test_auth_roles.py -v -s

# Generar reporte HTML
pytest tests/test_auth_roles.py -v --html=report.html
```

**Ejemplo de test que verifica autorización:**

```python
def test_admin_puede_acceder_todo(self, client: TestClient, setup_usuarios):
    """Test: Admin tiene acceso a todos los endpoints"""
    usuario = setup_usuarios["admin@test.com"]["usuario"]
    token = create_access_token(data={"sub": str(usuario.id_usuario)})
    
    response = client.get(
        "/usuarios/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Admin NO debe recibir 403
    assert response.status_code != 403
```

---

### ✅ 2. Logs Inteligentes: `app/core/segurity.py`

**Cambios realizados:**

- ❌ Reemplazado todos los `print()` con `logger` (logging module)
- ✅ Logs centralizados en puntos críticos
- ✅ Niveles apropiados: `logger.info()`, `logger.warning()`, `logger.error()`, `logger.debug()`
- ✅ NO logs excesivos (sin logs por cada request)

**Logger setup:**

```python
import logging

logger = logging.getLogger(__name__)

# En desarrollo:
logger.setLevel(logging.DEBUG)  # Ve logs DEBUG
logger.info("Usuario autenticado correctamente")  # Info importante
logger.warning("Token expirado")  # Advertencias
logger.error("Usuario no existe")  # Errores

# En producción:
logger.setLevel(logging.INFO)  # Solo INFO y superior
```

**Logs en puntos clave:**

| Evento | Nivel | Ejemplo |
|--------|-------|---------|
| Login exitoso | `INFO` | `"Login exitoso \| Usuario: admin@test.com \| Rol: admin"` |
| Email no existe | `WARNING` | `"Intento de login con email no existente: xxx@test.com"` |
| Contraseña incorrecta | `WARNING` | `"Intento de login con contraseña incorrecta: admin@test.com"` |
| Token expirado | `WARNING` | `"Intento de acceso con token expirado"` |
| Token inválido | `WARNING` | `"Token malformado o inválido"` |
| Usuario no existe en BD | `WARNING` | `"Usuario no existe en BD. ID: 123"` |
| Acceso denegado por rol | `WARNING` | `"Acceso denegado - se requiere ADMIN. Usuario: vigilante@test.com"` |
| Validación JWT | `DEBUG` | `"Token decodificado exitosamente. Sub: 5, Exp: 1712000000"` |

**Configurar logging en `app/main.py`:**

```python
import logging

# Configurar logging (agregar después de crear app)
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG en dev, INFO en prod
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),  # Guardar en archivo
        logging.StreamHandler()  # También mostrar en consola
    ]
)
```

---

### ✅ 3. Validaciones de Errores Comunes: `app/utils/auth_validators.py`

Módulo para detectar y diagnosticar errores comunes en JWT y autorización.

**Funciones disponibles:**

#### 📌 **Validación de Payload**

```python
from app.utils.auth_validators import validar_payload_jwt, detectar_campos_faltantes

# Validar que payload sea válido
es_valido, msg = validar_payload_jwt(payload)
if not es_valido:
    logger.error(f"Payload inválido: {msg}")

# Detectar campos específicos faltantes
faltantes = detectar_campos_faltantes(payload, ["sub", "rol", "email"])
if faltantes:
    logger.error(faltantes)
```

#### 📌 **Validación de Tipos**

```python
from app.utils.auth_validators import validar_tipo_sub

# Validar que 'sub' (usuario ID) sea int o string convertible
es_valido, msg = validar_tipo_sub(payload.get("sub"))
if not es_valido:
    logger.error(f"Campo 'sub' inválido: {msg}")
```

**Detecta:**

- ✅ `sub` como float, list, dict (tipos inválidos)
- ✅ `sub` como string pero contiene caracteres no numéricos
- ✅ `sub` como int pero es negativo o cero
- ✅ `sub` None o vacío

#### 📌 **Validación de Expiración**

```python
from app.utils.auth_validators import (
    detectar_token_casi_expirado,
    validar_timestamp_exp
)

# Detectar si token expira pronto
casi_expirado, msg = detectar_token_casi_expirado(
    payload.get("exp"),
    umbral_segundos=300  # Alerta si expira en menos de 5 min
)
if casi_expirado:
    logger.warning(msg)  # Output: "Token expirará en 120 segundos"

# Validar timestamp válido
es_valido, msg = validar_timestamp_exp(payload.get("exp"))  # Rango 1970-2100
```

#### 📌 **Validación de Header Authorization**

```python
from app.utils.auth_validators import validar_header_authorization

# Validar header formato
es_valido, msg = validar_header_authorization(request.headers.get("Authorization"))
if not es_valido:
    logger.error(f"Header inválido: {msg}")
```

**Detecta:**

- ✅ Header vacío o None
- ✅ Sin "Bearer" al inicio (`Authorization: token123` en lugar de `Bearer token123`)
- ✅ Token vacío después de Bearer (`Authorization: Bearer`)
- ✅ Schema incorrecto (`Authorization: Basic token123`)

#### 📌 **Validación de Roles**

```python
from app.utils.auth_validators import (
    validar_rol_existe_en_bd,
    detectar_permisos_excesivos
)

# Validar que rol en BD coincida con token
es_valido, msg = validar_rol_existe_en_bd(
    usuario_rol_db="docente",
    rol_en_payload="admin"  # ⚠️ No coinciden
)  # Output: False, "Rol de usuario no coincide..."

# Detectar si token tiene permisos no autorizados (token modificado)
excesivos = detectar_permisos_excesivos(
    usuario_permisos_db=["ver_estudiantes", "crear_estudiante"],
    permisos_payload=["ver_estudiantes", "admin_full_access"]  # ⚠️
)
if excesivos:
    logger.error(f"Token modificado/falsificado: {excesivos}")
```

#### 📌 **Diagnóstico Completo**

```python
from app.utils.auth_validators import diagnosticar_token_problemas

# Ejecutar diagnóstico completo
problemas = diagnosticar_token_problemas(
    payload=payload,
    auth_header="Bearer ey...",
    usuario_rol_db="docente",
    usuario_permisos_db=["ver_estudiantes"]
)

if problemas:
    for problema in problemas:
        logger.error(f"Problema detectado: {problema}")
else:
    logger.info("Token sin problemas detectados")
```

---

## 🚀 EJEMPLO DE USO COMPLETO

### Caso 1: Detectar Swagger usando Token Viejo

```python
from app.utils.auth_validators import diagnosticar_token_problemas
from app.core.segurity import decode_token

# En un endpoint protegido:
@router.get("/usuarios/")
def listar_usuarios(current_user = Depends(get_current_user), db=Depends(get_db)):
    # Diagnosticar el token
    auth_header = request.headers.get("Authorization")
    payload = decode_token(extractar_token(auth_header))
    
    problemas = diagnosticar_token_problemas(
        payload=payload,
        auth_header=auth_header,
        usuario_rol_db=current_user.get("rol"),
        usuario_permisos_db=current_user.get("permisos")
    )
    
    if problemas:
        logger.warning(f"Problemas detectados en token de {current_user['email']}: {problemas}")
    
    # ... rest de lógica
```

### Caso 2: Validar en Login

```python
from app.utils.auth_validators import validar_tipo_sub

@router.post("/login")
def login(credenciales: LoginRequest, db=Depends(get_db)):
    usuario = obtener_usuario(credenciales.email)
    
    # Crear token
    token_payload = {"sub": str(usuario.id_usuario)}
    
    # Validar antes de crear token
    es_valido, msg = validar_tipo_sub(token_payload["sub"])
    if not es_valido:
        logger.error(f"ID de usuario inválido: {msg}")
        raise HTTPException(status_code=500)
    
    access_token = create_access_token(token_payload)
    logger.info(f"Token generado para usuario {usuario.id_usuario}")
    
    return {"access_token": access_token, ...}
```

### Caso 3: Detección de Modificación de Token

```python
from app.utils.auth_validators import detectar_permisos_excesivos

@router.post("/registros/")
def crear_registro(
    data: dict,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    # Verificar que permisos en token no han sido modificados
    usuario_en_db = db.query(Usuario).get(current_user["id"])
    permisos_db = obtener_permisos(usuario_en_db.rol_id)
    
    excesivos = detectar_permisos_excesivos(
        permisos_db,
        current_user.get("permisos", [])
    )
    
    if excesivos:
        logger.error(f"ALERTA SEGURIDAD: Token modificado para {current_user['email']}")
        raise HTTPException(status_code=403, detail="Token inválido")
    
    # ... rest de lógica
```

---

## 🧪 EJECUTAR TESTS

### Setup inicial

```bash
# 1. Instalar dependencias de test
pip install pytest pytest-asyncio pytest-cov

# 2. Crear BD de test (SQLite en memoria, automática en tests)

# 3. Ejecutar tests
pytest tests/test_auth_roles.py -v
```

### Ejemplos de ejecución

```bash
# Todos los tests
pytest tests/test_auth_roles.py -v

# Solo tests de login
pytest tests/test_auth_roles.py::TestLogin -v

# Solo tests de errores comunes
pytest tests/test_auth_roles.py::TestCommonErrors -v -s

# Test específico
pytest tests/test_auth_roles.py::TestLogin::test_login_exitoso -v

# Con cobertura
pytest tests/test_auth_roles.py --cov=app.core.segurity --cov=app.routers.auth_router

# Ver qué está fallando
pytest tests/test_auth_roles.py -v --tb=short
```

---

## 📊 CONFIGURACIÓN DE LOGGING RECOMENDADA

### `app/main.py`

```python
from fastapi import FastAPI
import logging
import logging.config

# YAML config (create logging_config.yaml)
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "detailed",
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
        },
    },
    "loggers": {
        "app.core.segurity": {
            "handlers": ["default", "file"],
            "level": "INFO",
        },
        "app.routers.auth_router": {
            "handlers": ["default", "file"],
            "level": "INFO",
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

app = FastAPI()
```

---

## 🔍 ERRORES COMUNES DETECTADOS

| Error | Síntoma | Solución |
|-------|--------|----------|
| Token con `sub` como float | `"No se puede convertir 'sub' a int"` | Token generado incorrectamente |
| Payload sin `sub` | `"Campo 'sub' faltante en payload"` | Validar que `create_access_token` incluya `sub` |
| Header sin Bearer | `"Header Authorization mal formado"` | Cliente debe enviar `Authorization: Bearer ...` |
| Rol en token ≠ rol en BD | `"Rol de usuario no coincide"` | Token desactualizado, usuario cambió rol |
| Token casi vencido | `"Token expirará en 120 segundos"` | Advertencia para renovar token |
| Usuario eliminado después de login | `"Usuario no encontrado en BD"` | Token válido pero usuario no existe |
| Permisos excesivos en token | `"Token contiene permisos no autorizados"` | Token puede estar modificado/falsificado |

---

## 📝 ESTRUCTURA FINAL

```
app/
├── core/
│   ├── segurity.py              ← Mejorado con logging
│   ├── database.py
│   └── config.py
├── routers/
│   └── auth_router.py           ← Agregar logs en login
├── utils/
│   └── auth_validators.py       ← NUEVO: Validadores
├── models/
├── services/
└── main.py

tests/
└── test_auth_roles.py           ← NUEVO: Tests completos
```

---

## ✅ CHECKLIST

- [x] Tests con pytest creados
- [x] Logging reemplazando prints
- [x] Validadores de errores comunes
- [x] Documentación completa
- [x] Ejemplos de uso incluidos
- [x] Casos edge cubiertos
- [x] Roles y permisos testeados
- [x] Código listo para producción

---

**¡Listo para depuración y testing en producción!** 🚀
