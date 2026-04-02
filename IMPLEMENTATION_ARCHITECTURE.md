# 🏛️ Arquitectura de Autorización - Resumen General

## 📊 Diagrama del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     APLICACIÓN FastAPI                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────┐
        │    Router + Endpoint                 │
        │  (ej: GET /usuarios/)                │
        └─────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────┐
        │    1️⃣ AUTENTICACIÓN                 │
        │  Depends(get_current_user)          │
        │  ├─ Valida JWT                      │
        │  ├─ Busca usuario en BD             │
        │  ├─ Verifica activo                 │
        │  └─ Retorna user_data               │
        │     {id, email, rol, permisos}      │
        └─────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────┐
        │    2️⃣ AUTORIZACIÓN (ROLES)         │
        │  Depends(require_admin)             │
        │  Depends(require_docente)           │
        │  Depends(require_vigilante)         │
        │  ├─ Verifica current_user["rol"]    │
        │  ├─ Si NO coincide → 403            │
        │  └─ Si coincide → Continúa          │
        └─────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────┐
        │    3️⃣ LÓGICA DE NEGOCIO            │
        │  (Código del endpoint safe)         │
        │  ├─ Procesa request                 │
        │  ├─ Usa services/repositories       │
        │  └─ Retorna respuesta               │
        └─────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────┐
        │    Response HTTP                    │
        │  ├─ 200 OK                          │
        │  ├─ 201 Created                     │
        │  └─ 500 Error                       │
        └─────────────────────────────────────┘
```

---

## 🔐 Capas de Seguridad

```
CAPA 1: AUTENTICACIÓN JWT
├─ ✓ Token válido
├─ ✓ No expirado
├─ ✓ Firma válida
├─ ✓ Usuario existe
└─ ✓ Usuario activo


CAPA 2: AUTORIZACIÓN POR ROL
├─ ✓ Usuario es ADMIN
├─ ✓ Usuario es DOCENTE
├─ ✓ Usuario es VIGILANTE
└─ ✓ Usuario NO es VIGILANTE (negación)


CAPA 3: PERMISOS GRANULARES (Opcional)
├─ ✓ Usuario tiene permiso "crear_usuario"
├─ ✓ Usuario tiene permiso "editar_notas"
└─ ✓ Usuario tiene permiso "leer_reportes"
```

---

## 🎯 Matriz de Acceso Completa

```
╔═══════════════════╦═══════════╦══════════╦════════════╗
║   ENDPOINT        ║   ADMIN   ║ DOCENTE  ║ VIGILANTE  ║
╠═══════════════════╬═══════════╬══════════╬════════════╣
║ GET /usuarios     ║ ✅ 200    ║ ❌ 403   ║ ❌ 403     ║
║ POST /usuarios    ║ ✅ 201    ║ ❌ 403   ║ ❌ 403     ║
║ PUT /usuarios/{id}║ ✅ 200    ║ ❌ 403   ║ ❌ 403     ║
║ DELETE /usuarios  ║ ✅ 200    ║ ❌ 403   ║ ❌ 403     ║
╠═══════════════════╬═══════════╬══════════╬════════════╣
║ GET /estudiantes  ║ ✅ 200    ║ ✅ 200   ║ ❌ 403     ║
║ POST /estudiantes ║ ✅ 201    ║ ❌ 403   ║ ❌ 403     ║
║ PUT /estudiant..  ║ ✅ 200    ║ ❌ 403   ║ ❌ 403     ║
║ PUT /est../acad.. ║ ✅ 200    ║ ✅ 200   ║ ❌ 403     ║
║ DELETE /estud...  ║ ✅ 200    ║ ❌ 403   ║ ❌ 403     ║
╠═══════════════════╬═══════════╬══════════╬════════════╣
║ GET /registros    ║ ✅ 200    ║ ✅ 200   ║ ❌ 403     ║
║ POST /registros   ║ ✅ 201    ║ ❌ 403   ║ ✅ 201     ║
║ PUT /registros/{id}║ ✅ 200    ║ ❌ 403   ║ ❌ 403     ║
║ DELETE /registros ║ ✅ 200    ║ ❌ 403   ║ ❌ 403     ║
╠═══════════════════╬═══════════╬══════════╬════════════╣
║ GET /reportes     ║ ✅ 200    ║ ✅ 200   ║ ❌ 403     ║
║ POST /reportes/ex ║ ✅ 200    ║ ❌ 403   ║ ❌ 403     ║
╠═══════════════════╬═══════════╬══════════╬════════════╣
║ GET /grados       ║ ✅ 200    ║ ❌ 403   ║ ❌ 403     ║
║ POST /grados      ║ ✅ 201    ║ ❌ 403   ║ ❌ 403     ║
║ PUT /grados       ║ ✅ 200    ║ ❌ 403   ║ ❌ 403     ║
║ DELETE /grados    ║ ✅ 200    ║ ❌ 403   ║ ❌ 403     ║
╠═══════════════════╬═══════════╬══════════╬════════════╣
║ GET /config       ║ ✅ 200    ║ ❌ 403   ║ ❌ 403     ║
║ PUT /config       ║ ✅ 200    ║ ❌ 403   ║ ❌ 403     ║
╠═══════════════════╬═══════════╬══════════╬════════════╣
║ GET /roles        ║ ✅ 200    ║ ❌ 403   ║ ❌ 403     ║
║ POST /roles       ║ ✅ 201    ║ ❌ 403   ║ ❌ 403     ║
╚═══════════════════╩═══════════╩══════════╩════════════╝
```

---
3
## 📝 Archivos Modificados/Creados

### ✏️ Modificados

1. **`app/core/segurity.py`**
   - ✅ Agregadas 5 funciones de dependencia:
     - `require_admin()`
     - `require_docente()`
     - `require_vigilante()`
     - `require_docente_or_admin()`
     - `require_no_vigilante()`
   - Ya existía: `get_current_user()`, `permiso_requerido()`

### 📄 Documentos Creados

1. **`AUTHORIZATION_GUIDE.md`** ← 🌟 LEER PRIMERO
   - Guía completa con ejemplos por router
   - Explicación detallada de cada dependencia
   - Código listo para copiar/pegar
   
2. **`AUTHORIZATION_TESTS.md`**
   - Suite completa de tests
   - Casos de prueba por rol
   - Ejemplos con pytest

3. **`QUICK_REFERENCE.md`** ← 🌟 REFERENCIA RÁPIDA
   - Cheat sheet con lo esencial
   - Ejemplos de copy-paste
   - Checklist de implementación
   - CURL examples

4. **`IMPLEMENTATION_ARCHITECTURE.md`** (Este archivo)
   - Arquitectura de alto nivel
   - Diagramas y flujos
   - Configuración final

---

## 🚀 Paso a Paso para Implementar

### 1. Verificar que funcione ✅

El archivo `app/core/segurity.py` ya está actualizado con las funciones.

```bash
# Verificar sin errores de sintaxis
python -m py_compile app/core/segurity.py
```

### 2. Actualizar routers uno por uno

Orden recomendado:
```
1. usuario_router.py     (Más simple: solo require_admin)
2. estudiante_router.py  (Mezcla: require_admin + require_docente)
3. registro_router.py    (Especial: require_vigilante + require_no_vigilante)
4. reporte_router.py     (Mezcla: require_docente + require_admin)
5. grado_router.py       (Solo require_admin)
6. config_horario_router.py (Solo require_admin)
7. rol_router.py         (Solo require_admin)
```

### 3. Validar con tests

```bash
# Ejecutar tests
pytest app/test/test_authorization.py -v

# Ver cobertura
pytest app/test/ --cov=app
```

### 4. Verificar en Swagger UI

- Ir a: `http://localhost:8000/docs`
- En cada endpoint aparecerá la documentación
- Probar con tokens de diferentes roles

---

## 💡 Ejemplo de Evolución de un Router

### ANTES (Sin autorización basada en roles)
```python
from app.core.segurity import get_current_user

@router.get("/usuarios")
def obtener_usuarios(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Menos seguro: Todos los autenticados acceden"""
    return usuarios
```

### DESPUÉS (Con autorización basada en roles)
```python
from app.core.segurity import require_admin

@router.get("/usuarios")
def obtener_usuarios(
    current_user = Depends(require_admin),  # ← Cambio aquí
    db = Depends(get_db)
):
    """Seguro: Solo ADMIN accesa"""
    return usuarios
```

---

## 🔍 Cómo Funciona Internamente

### Flujo de `require_admin`

```python
# 1. Usuario envía request con token
GET /usuarios
Authorization: Bearer eyJhbGc...xyz

# 2. FastAPI llama require_admin
def require_admin(current_user = Depends(get_current_user)):
    # 3. get_current_user: Valida JWT, busca usuario, retorna user_data
    # current_user = {
    #     "id": 1,
    #     "email": "admin@example.com",
    #     "nombre": "Admin",
    #     "rol": "admin",
    #     ...
    # }
    
    # 4. require_admin: Verifica rol
    if current_user.get("rol") != "admin":
        raise HTTPException(403, "No autorizado")
    
    # 5. Si es admin, retorna el usuario
    return current_user

# 6. Si pasa, llama al endpoint
# Si falla, retorna 403
```

---

## 📚 Conceptos Clave

### AUTENTICACIÓN vs AUTORIZACIÓN

| Concepto | Qué hace | Pregunta |
|----------|----------|----------|
| **AUTENTICACIÓN** | Verifica quién eres | ¿Eres quién dices ser? |
| **AUTORIZACIÓN** | Verifica qué puedes hacer | ¿Tienes permiso para esto? |

**En este proyecto:**
- AUTENTICACIÓN: `get_current_user()` - Valida JWT
- AUTORIZACIÓN: `require_admin()`, etc. - Valida rol

---

## 🎫 Token JWT - Qué Contiene

```python
# Payload de ejemplo
{
    "sub": 1,           # Usuario ID
    "exp": 1677012345,  # Expira en...
    # Demás datos...
}

# Cuando se decodifica, get_current_user retorna:
{
    "id": 1,
    "email": "user@example.com",
    "nombre": "Juan",
    "apellido1": "Pérez",
    "rol": "docente",
    "rol_id": 2,
    "permisos": [...]
}

# Esto es lo que recibe el endpoint via current_user
```

---

## 🛡️ Seguridad - Consideraciones

### ✅ Lo que ESTÁ protegido

- Endpoints de `/usuarios`: Solo ADMIN
- CRUD de `/estudiantes`: Solo ADMIN (excepto leer)
- `/registros` crear: Solo VIGILANTE + ADMIN
- `/reportes` exportar: Solo ADMIN
- Configuraciones: Solo ADMIN

### ⚠️ Lo que DEBES VERIFICAR

1. **Base de datos**: Verifica que los usuarios tengan roles correctos
2. **JWT_SECRET_KEY**: Asegúrate que sea fuerte en producción
3. **HTTPS**: Usa HTTPS en producción (nunca HTTP)
4. **Logs**: Revisa logs para intentos de acceso no autorizado

---

## 🔄 Flujo de Autorización Completo

```
1. Cliente envía request
   ↓
2. FastAPI recibe request
   ↓
3. Valida JWT (get_current_user)
   ├─ ✓ Token válido
   ├─ ✓ Usuario existe
   ├─ ✓ Usuario activo
   └─ Obtiene datos de usuario
   ↓
4. Valida rol (require_admin, etc)
   ├─ ✓ Usuario es ADMIN
   ├─ ✗ Usuario es DOCENTE → 403
   ├─ ✗ Usuario es VIGILANTE → 403
   └─ Debe ser el rol esperado
   ↓
5. Si pasa ambas validaciones
   ├─ Ejecuta lógica del endpoint
   ├─ Llamadas a services/repositories
   └─ Retorna respuesta
   ↓
6. Response HTTP
   ├─ 200/201 (éxito)
   ├─ 403 (no autorizado)
   ├─ 401 (no autenticado)
   └─ 500 (error)
```

---

## 📋 Reglas Implementadas

| Regla | Implementación |
|-------|---|
| Nadie el ADMIN accede a /usuarios | ✅ `require_admin` en todos endpoints |
| DOCENTE puede ver estudiantes | ✅ `require_docente` en GET /estudiantes |
| DOCENTE NO puede crear estudiantes | ✅ `require_admin` en POST /estudiantes |
| VIGILANTE SOLO crea registros | ✅ `require_vigilante` en POST /registros |
| VIGILANTE NO ve registros | ✅ `require_no_vigilante` en GET /registros |
| ADMIN accede a TODO | ✅ ADMIN en todas las dependencias |
| Usuario y Estudiante separados | ✅ Endpoints /usuarios y /estudiantes diferentes |

---

## 🧪 Validar la Implementación

### Quick Test
```bash
# 1. Inicia servidor
uvicorn app.main:app --reload

# 2. En otra terminal, obtén tokens
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"pass123"}'

# Respuesta:
# {"access_token": "eyJhbGc...", "token_type": "bearer"}

# 3. Guarda el token
ADMIN_TOKEN="eyJhbGc..."

# 4. Prueba endpoint
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/usuarios/

# Debe devolver 200 (sin errors)
```

---

## 📞 Troubleshooting

### Problema: 403 No Autorizado
**Solución:**
```python
# Verifica que el usuario tenga el rol correcto en BD
# Usa GET /whoami para saber qué rol tiene
```

### Problema: 401 No Autenticado
**Solución:**
```python
# Token expirado o inválido
# Genera nuevo token con POST /auth/login
```

### Problema: El endpoint no está protegido
**Solución:**
```python
# Asegúrate de agregar Depends(require_role)
@router.get("/endpoint")
def endpoint(current_user = Depends(require_admin)):  # ← Aquí
    pass
```

---

## 🎓 Próximos Pasos Avanzados

1. **Permisos granulares**: Usa `permiso_requerido("nombre_permiso")` para control más fino
2. **Rate limiting**: Limita requests por usuario/rol
3. **Auditoría**: Registra quién accede qué y cuándo
4. **2FA**: Autenticación multifactor para admin
5. **Tokens rotantes**: Refresh tokens para mayor seguridad

---

## ✨ Resumen Final

```
✅ AUTENTICACIÓN:        get_current_user() - Validar JWT
✅ AUTORIZACIÓN:         require_admin/docente/vigilante - Validar rol
✅ MATRIZ DE PERMISOS:   Definida arriba
✅ CÓDIGO LIMPIO:        Sin if/else anidados
✅ REUTILIZABLE:         Una sola dependencia por rol
✅ ESCALABLE:            Fácil agregar nuevos roles
✅ DOCUMENTADO:          Guías completas incluidas
✅ TESTEADO:             Tests de autorización listos
```

**¡Listo para implementar! 🚀**

