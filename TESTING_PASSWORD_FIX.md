# Testing Password Validation Fix - Paso a Paso

## 📋 Resumen de Cambios Realizados

### ✅ Problema Raíz Identificado
- **Pydantic v2** instalado, pero código usando **Pydantic v1** decoradores
- `@validator` **NO SE EJECUTABA** en Pydantic v2
- Contraseñas iban directamente a bcrypt sin validar
- bcrypt rechazaba con error: "password cannot be longer than 72 bytes"

### ✅ Solución Aplicada (4 Archivos)

| Archivo | Cambio | Razón |
|---------|--------|-------|
| `app/schemas/usuario.py` | `@validator` → `@field_validator` | Pydantic v2 syntax |
| `app/schemas/auth.py` | `@validator` → `@field_validator` | Pydantic v2 syntax |
| `app/core/segurity.py` | Agregué debugging detallado | Ver dónde falla |
| `app/services/usuario_service.py` | Agregué debugging detallado | Trazar ejecución |

---

## 🧪 Paso 1: Preparar el Ambiente

### En terminal (Backend):
```bash
cd c:\Users\Nelson Pinzón\Desktop\Proyecto\Media-tecnica-Backend

# Asegúrate que la venv esté activa
python -m pip list | findstr pydantic

# Debería mostrar: pydantic 2.x.x
```

---

## 🚀 Paso 2: Reiniciar FastAPI con Debugging

### Detener la instancia actual (si corre):
```
Ctrl+C en la terminal donde corre FastAPI
```

### Iniciar nuevo con recargar automático:
```bash
python -m uvicorn app.main:app --reload
```

**Esperado en terminal:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

---

## 🧬 Paso 3: Ejecutar Tests

### En OTRA terminal (Terminal 2):
```bash
cd c:\Users\Nelson Pinzón\Desktop\Proyecto\Media-tecnica-Backend
python test_password_simple.py
```

---

## 📊 Interpretar Resultados

### Test 1: Contraseña Válida (Corta)
```
[TEST 1] Contraseña VÁLIDA (corta - 10 bytes)
Email: test1-[timestamp]@example.com
Contraseña: MyPass123!
Caracteres: 10
Bytes UTF-8: 10
```

**En Terminal 1 (FastAPIl) Deberías ver:
```
[VALIDATOR] campo: contrasena
[VALIDATOR] valor: MyPass123!
[VALIDATOR] chars: 10
[VALIDATOR] bytes: 10
[HASH] Iniciando hash_password
[HASH] Bytes validados: 10 <= 72 ✓
[HASH] Hash creado exitosamente
```

**En Terminal 2 (Test Output) Deberías ver:**
```
Status Code: 201
✅ ÉXITO - Usuario creado
```

---

### Test 2: Contraseña Válida (Con Acentos)
```
[TEST 2] Contraseña VÁLIDA (con acentos - 13 caracteres/15 bytes)
Contraseña: Contraseña123
Bytes UTF-8: 15
```

**En Terminal 1 Deberías ver:**
```
[VALIDATOR] chars: 13
[VALIDATOR] bytes: 15
[VALIDATOR] Validación OK
[HASH] Bytes validados: 15 <= 72 ✓
```

**En Terminal 2 Deberías ver:**
```
Status Code: 201
✅ ÉXITO - Usuario creado
```

---

### Test 3: Contraseña INVÁLIDA (Unicode Larga - Excede 72 bytes)
```
[TEST 3] Contraseña INVÁLIDA (Unicode larga - 40 caracteres/120 bytes)
Contraseña: 中文密码中文密码中文密码...
Bytes UTF-8: 120
```

**En Terminal 1 Deberías ver:**
```
[VALIDATOR] chars: 40
[VALIDATOR] bytes: 120
[VALIDATOR] ❌ RECHAZO: contrasena excede 72 bytes (120 bytes)
```

**En Terminal 2 Deberías ver:**
```
Status Code: 422
Response: {
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "contrasena"],
      "msg": "Contraseña excede 72 bytes (120 bytes). Máximo: 72 bytes",
      "input": "中文密码中文密码..."
    }
  ]
}
✅ CORRECTO - Rechazada como debe ser
```

---

### Test 4: Login
```
[TEST 4] Login con Contraseña Válida
```

**En Terminal 1 Deberías ver:**
```
[EMAIL LOGIN ATTEMPT] email: test1-[timestamp]@example.com
[HASH COMPARISON] Comparando password...
[LOGIN SUCCESS] Token generado
```

**En Terminal 2 Deberías ver:**
```
Status Code: 200
✅ ÉXITO - Token recibido
```

---

## ✔️ Checklist de Validación

- [ ] Terminal 1 muestra "[VALIDATOR]" al crear usuario
- [ ] Terminal 1 muestra "[HASH]" al validar bytes
- [ ] Test 1 ve 201 (password corta, válida)
- [ ] Test 2 ve 201 (password con acentos, válida)
- [ ] Test 3 ve 422 (password larga Unicode, inválida)
- [ ] Test 4 ve 200 con token (login funciona)

---

## 🔍 Troubleshooting

### Si aún ves "password cannot be longer than 72 bytes":
1. **Verificar que FastAPI se reinició:** ¿Ves el mensaje de reload?
2. **Verificar imports:** En Terminal 1, busca `[VALIDATOR]` - si no aparece, validadores aún no se ejecutan
3. **Verificar Python:** `python --version` debe ser 3.8+

### Si ves "ModuleNotFoundError":
```bash
pip install -r requirements.txt
```

### Si ves "Connection refused":
```bash
# FastAPI no está corriendo
python -m uvicorn app.main:app --reload
```

---

## 📝 Notas Importantes

1. **Los prints [VALIDATOR], [HASH], [SERVICE] son temporales** para debugging
2. Una vez verificado que funciona, podemos eliminarlos
3. **La validación ocurre en 2 capas:**
   - SCHEMA (contrasena) - rechaza en pydantic (422)
   - SECURITY (hash_password) - rechaza con ValueError
4. **Ambas capas están activas** para máxima seguridad

---

## ✅ Éxito Confirmado Cuando:

✔️ Las contraseñas válidas crean usuarios exitosamente
✔️ Las contraseñas inválidas (>72 bytes) son rechazadas ANTES de llegar a bcrypt
✔️ Los errores son claros: "Contraseña excede 72 bytes"
✔️ Login funciona con contraseñas válidas

---

**¿Listo?** 
1. Abre 2 terminales (Terminal 1: FastAPI, Terminal 2: Tests)
2. `python -m uvicorn app.main:app --reload`
3. `python test_password_simple.py`
4. Comparte el output de AMBAS terminales
