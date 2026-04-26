# 🔐 Solución: Error "password cannot be longer than 72 bytes"

## 🎯 Problema Identificado

**Error:** `password cannot be longer than 72 bytes`

**Causa Real:** bcrypt tiene un límite DURO de 72 bytes. Cuando una contraseña en texto plano se envía al hash_password(), si excede 72 bytes en UTF-8, bcrypt rechaza la operación.

**Por qué pasaba:**
- El schema permitía `max_length=255` caracteres
- 255 caracteres de Unicode = hasta 600+ bytes en UTF-8
- Cuando llegaba al bcrypt, este rechazaba la contraseña

---

## ✅ Soluciones Implementadas

### 1. **Validación en Schemas (Primera Línea de Defensa)**

#### `app/schemas/usuario.py`
```python
class UsuarioCreate(UsuarioBase):
    """Schema para crear Usuario"""
    contrasena: str = Field(..., min_length=8, max_length=72)  # ← 72 caracteres máximo
    
    @validator('contrasena')
    def validar_contrasena_bytes(cls, v):
        """Validar que la contraseña no exceda 72 bytes en UTF-8"""
        bytes_length = len(v.encode('utf-8'))
        if bytes_length > 72:
            raise ValueError(
                f"La contraseña no puede exceder 72 bytes en UTF-8 "
                f"(recibido: {bytes_length} bytes). "
                f"Usa contraseñas más simples o más cortas."
            )
        return v
```

#### `app/schemas/auth.py`
```python
class LoginRequest(BaseModel):
    """Schema para Login"""
    email: EmailStr
    contraseña: str = Field(..., min_length=8, max_length=72)  # ← 72 caracteres máximo
    
    @validator('contraseña')
    def validar_contrasena_bytes(cls, v):
        """Validar que la contraseña no exceda 72 bytes en UTF-8"""
        if len(v.encode('utf-8')) > 72:
            raise ValueError(
                f"La contraseña no puede exceder 72 bytes en UTF-8 (recibido: {len(v.encode('utf-8'))} bytes)"
            )
        return v
```

### 2. **Validación Robusta en hash_password() (Segunda Línea)**

#### `app/core/segurity.py`
```python
def hash_password(password: str) -> str:
    """
    Hashear una contraseña usando bcrypt.
    
    IMPORTANTE: bcrypt tiene un límite DURO de 72 bytes.
    """
    if not isinstance(password, str):
        logger.error(f"hash_password recibió tipo incorrecto: {type(password).__name__}")
        raise ValueError(f"La contraseña debe ser texto plano (string)")
    
    # Validar longitud en BYTES (no caracteres)
    bytes_length = len(password.encode('utf-8'))
    
    logger.debug(f"hash_password - Longitud: {len(password)} caracteres, {bytes_length} bytes UTF-8")
    
    if bytes_length > 72:
        logger.error(f"Contraseña que excede 72 bytes: {bytes_length} bytes")
        raise ValueError(
            f"La contraseña excede el límite de 72 bytes en UTF-8 "
            f"(tiene {bytes_length} bytes)."
        )
    
    try:
        hashed = pwd_context.hash(password)
        logger.debug("Contraseña hasheada exitosamente")
        return hashed
    except Exception as e:
        logger.error(f"Error al hashear: {str(e)}")
        raise ValueError(f"Error al procesar la contraseña: {str(e)}")
```

### 3. **Mejor Logging y Documentación en usuario_service.py**

La función `crear_usuario()` ahora:
- ✅ Extrae la contraseña en TEXTO PLANO (del Schema pydantic)
- ✅ Valida que sea string
- ✅ Valida longitud en bytes
- ✅ Hashea UNA SOLA VEZ
- ✅ Guarda SOLO el hash (nunca la contraseña en plano)
- ✅ Logging detallado en cada paso

---

## 🧪 Testing Manual

### Escenario 1: Contraseña Válida (8-20 caracteres ASCII)

```bash
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan",
    "apellido1": "Pérez",
    "correo": "juan@example.com",
    "contrasena": "MyPass123!",
    "rol_id": 1
  }'
```

**Resultado esperado:** ✅ Usuario creado exitosamente

---

### Escenario 2: Contraseña Demasiado Corta (< 8 caracteres)

```bash
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan",
    "apellido1": "Pérez",
    "correo": "juan@example.com",
    "contrasena": "abc123",
    "rol_id": 1
  }'
```

**Resultado esperado:** ❌ Error 422 - "ensure this value has at least 8 characters"

---

### Escenario 3: Contraseña con Muchos Caracteres Unicode

```bash
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan",
    "apellido1": "Pérez",
    "correo": "juan@example.com",
    "contrasena": "中文密码1234567890中文密码1234567890",
    "rol_id": 1
  }'
```

**Resultado esperado:** ❌ Error 422 - "La contraseña no puede exceder 72 bytes en UTF-8"

**Por qué:** Cada carácter chino = 3-4 bytes en UTF-8

---

### Escenario 4: Login con Contraseña Válida

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@example.com",
    "contraseña": "MyPass123!"
  }'
```

**Resultado esperado:** ✅ Token retornado

---

### Escenario 5: Login con Contraseña Demasiado Larga

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@example.com",
    "contraseña": "中文密码1234567890中文密码1234567890"
  }'
```

**Resultado esperado:** ❌ Error 422 - "La contraseña no puede exceder 72 bytes en UTF-8"

---

## 🔍 Debugging

### Ver logs cuando se crea usuario

En tu terminal donde corre FastAPI, deberías ver:

```
INFO:app.services.usuario_service:Creando usuario: juan@example.com
DEBUG:app.services.usuario_service:Validando contraseña para juan@example.com: Longitud=10 caracteres, Bytes UTF-8=10
DEBUG:app.core.segurity:hash_password - Longitud: 10 caracteres, 10 bytes UTF-8
DEBUG:app.core.segurity:Contraseña hasheada exitosamente
DEBUG:app.services.usuario_service:Contraseña hasheada exitosamente para juan@example.com
INFO:app.services.usuario_service:Usuario creado exitosamente: juan@example.com (ID: 1)
```

### Ver si hay problema con caracteres Unicode

Si alguien intenta una contraseña Unicode larga:

```
INFO:app.services.usuario_service:Creando usuario: test@example.com
DEBUG:app.services.usuario_service:Validando contraseña para test@example.com: Longitud=40 caracteres, Bytes UTF-8=120
WARNING:app.core.segurity:La contraseña excede el límite de 72 bytes en UTF-8 (tiene 120 bytes)
```

---

## 📊 Entendiendo UTF-8 bytes

| Carácter | Bytes | Ejemplo |
|----------|-------|---------|
| ASCII | 1 byte | `a`, `1`, `!` |
| Acentos | 2 bytes | `ñ`, `é`, `ü` |
| Chino/Japonés | 3-4 bytes | `中`, `日`, `文` |
| Emoji | 4 bytes | `🔐`, `💻`, `🚀` |

**Ejemplos de Longitud:**
- `password123` = 11 caracteres = 11 bytes = ✅ Válido
- `contraseña123` = 13 caracteres = 15 bytes = ✅ Válido
- `密码123` = 5 caracteres = 11 bytes = ✅ Válido
- `中文密码中文密码中文密码中文密码` = 16 caracteres = 48 bytes = ✅ Válido  
- `中文密码中文密码中文密码中文密码中文密码1234567` = 22 caracteres = 75 bytes = ❌ **Inválido**

---

## 🧑‍💻 Recomendaciones para el Frontend

### React / JavaScript

```javascript
// Validar contraseña ANTES de enviar al backend
function validarContraseña(password) {
  const bytesLength = new Blob([password]).size;  // Tamaño en bytes UTF-8
  
  if (password.length < 8) {
    return { valido: false, error: "Mínimo 8 caracteres" };
  }
  
  if (bytesLength > 72) {
    return { 
      valido: false, 
      error: `Contraseña demasiado larga (${bytesLength} bytes, máximo 72)` 
    };
  }
  
  return { valido: true };
}

// Usar en formulario
const resultado = validarContraseña(passwordInput.value);
if (!resultado.valido) {
  mensajeError.textContent = resultado.error;
  return;
}
```

---

## 🔒 Seguridad - Flujo Correcto

```
USUARIO INGRESA CONTRASEÑA
        ↓
FRONTEND VALIDA (opcional, UX)
- Mínimo 8 caracteres
- No exceda 72 bytes
        ↓
ENVÍA POR HTTPS
- Email + Contraseña en texto plano (es OK, está en HTTPS)
        ↓
BACKEND RECIBE
        ↓
PYDANTIC VALIDA (Schema)
- Email válido (EmailStr)
- Contraseña 8-72 caracteres
- Contraseña NO excede 72 bytes (validator)
        ↓
SI PASA → SERVICIO PROCESA
- Extrae contraseña en plano
- Valida tipo (string)
- Valida bytes
- Hashea con bcrypt
- Guarda HASH en BD (nunca la contraseña)
        ↓
BD GUARDA
- contrasena_hash: "$2b$12$..." (60 caracteres, hash bcrypt)
```

---

## 📝 Cambios Realizados - Resumen

| Archivo | Cambio | Razón |
|---------|--------|-------|
| `app/schemas/usuario.py` | Agregado `max_length=72` y `@validator` | Validar en input |
| `app/schemas/auth.py` | Agregado `max_length=72` y `@validator` | Validar en login |
| `app/core/segurity.py` | Mejorada `hash_password()` con validación | Segunda línea de defensa |
| `app/services/usuario_service.py` | Mejorado `crear_usuario()` con logging | Documentar el flujo |

---

## ✨ Beneficios de Esta Solución

✅ **Primera línea de defensa** - Pydantic valida antes de procesar  
✅ **Error claro** - Usuario recibe mensaje específico, no error genérico de bcrypt  
✅ **Logging detallado** - Puedes debuggear fácilmente  
✅ **Sin doble hash** - Solo se hashea UNA VEZ  
✅ **Seguridad** - Hash nunca se guarda en plano  
✅ **Funciona con Unicode** - Detecta caracteres especiales  
✅ **Cumple bcrypt** - Respeta strictamente el límite de 72 bytes

---

## ¿Ahora qué?

1. **Reinicia FastAPI:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. **Prueba los escenarios de arriba**

3. **Ver logs en tu terminal** para verificar que todo valida correctamente

4. **Ahora el frontend recibe errores claros** como:
   - `"ensure this value has at least 8 characters"`
   - `"La contraseña no puede exceder 72 bytes en UTF-8 (recibido: 120 bytes)"`

5. **Ya NO verás** el error genérico de bcrypt: `"password cannot be longer than 72 bytes"`

---

## 🚀 Problema Resuelto

El error ahora se **preventing proactivamente** en:
1. ✅ Schema Pydantic (validador)
2. ✅ Función hash_password (validación defensiva)
3. ✅ Servicio usuario (logging)

Y el usuario recibe un **mensaje claro y útil** en lugar del error genérico de bcrypt.

---

**¡Listo!** Tu backend está protegido contra contraseñas demasiado largas. 🔐
