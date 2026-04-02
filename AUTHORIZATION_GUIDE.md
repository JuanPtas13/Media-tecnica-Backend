# 🔐 Guía de Autorización Basada en Roles

## Estructura de Roles Implementada

```
ADMIN          → Acceso total a TODO
│
├── DOCENTE     → Acceso a estudiantes y reportes académicos
│
└── VIGILANTE   → Acceso SOLO a crear registros
```

---

## Dependencias Disponibles

### 1. `require_admin`
- Requiere rol: **ADMIN**
- Solo el administrador puede acceder
- Típicamente: CRUD de usuarios, configuraciones, gestión de roles

### 2. `require_docente`  
- Requiere rol: **DOCENTE** o **ADMIN**
- Admin también tiene acceso automáticamente
- Típicamente: Ver estudiantes, actualizar calificaciones, ver reportes

### 3. `require_vigilante`
- Requiere rol: **VIGILANTE** o **ADMIN**  
- Admin también tiene acceso automáticamente
- Típicamente: Crear registros de entrada/salida

### 4. `require_docente_or_admin`
- Requiere rol: **DOCENTE** o **ADMIN**
- Mismo que `require_docente`, pero más explícito

### 5. `require_no_vigilante`
- Niega acceso a: **VIGILANTE**
- Permite: **DOCENTE** y **ADMIN**
- Típicamente: Ver reportes, ver registros, etc.

---

## 🚀 Cómo Usar

### Import Necesario
```python
from app.core.segurity import (
    get_current_user,
    require_admin,
    require_docente,
    require_vigilante,
    require_docente_or_admin,
    require_no_vigilante
)
```

---

## 📋 Implementación en Routers

### 1. ROUTER DE USUARIOS (`usuario_router.py`)

**Solo ADMIN puede acceder a todos los endpoints de usuarios**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import require_admin, get_current_user
from app.services.usuario_service import UsuarioService
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.utils.responses import success_response

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# ============ SOLO ADMIN ============

@router.get("/", response_model=dict)
def obtener_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Obtener lista de usuarios - SOLO ADMIN"""
    try:
        service = UsuarioService(db)
        usuarios = service.obtener_todos(skip, limit)
        
        return success_response(
            data=usuarios,
            message="Usuarios obtenidos exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id_usuario}", response_model=dict)
def obtener_usuario(
    id_usuario: int,
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Obtener usuario por ID - SOLO ADMIN"""
    try:
        service = UsuarioService(db)
        usuario = service.obtener_por_id(id_usuario)
        
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return success_response(
            data=usuario,
            message="Usuario obtenido exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=dict)
def crear_usuario(
    usuario_in: UsuarioCreate,
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Crear nuevo usuario - SOLO ADMIN"""
    try:
        service = UsuarioService(db)
        nuevo_usuario = service.crear(usuario_in)
        
        return success_response(
            data=nuevo_usuario,
            message="Usuario creado exitosamente",
            status_code=201
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id_usuario}", response_model=dict)
def actualizar_usuario(
    id_usuario: int,
    usuario_update: UsuarioUpdate,
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Actualizar usuario - SOLO ADMIN"""
    try:
        service = UsuarioService(db)
        usuario_actualizado = service.actualizar(id_usuario, usuario_update)
        
        return success_response(
            data=usuario_actualizado,
            message="Usuario actualizado exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id_usuario}", response_model=dict)
def eliminar_usuario(
    id_usuario: int,
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Eliminar usuario - SOLO ADMIN"""
    try:
        service = UsuarioService(db)
        service.eliminar(id_usuario)
        
        return success_response(
            message="Usuario eliminado exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activos", response_model=dict)
def obtener_usuarios_activos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Obtener usuarios activos - SOLO ADMIN"""
    try:
        service = UsuarioService(db)
        usuarios = service.obtener_activos(skip, limit)
        
        return success_response(
            data=usuarios,
            message="Usuarios activos obtenidos exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### 2. ROUTER DE ESTUDIANTES (`estudiante_router.py`)

**ADMIN: CRUD completo | DOCENTE: Leer y actualizar**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import (
    require_admin,
    require_docente,
    require_no_vigilante
)
from app.services.estudiante_service import EstudianteService
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate, EstudianteResponse
from app.utils.responses import success_response

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])


# ============ ADMIN + DOCENTE ============
# Ambos pueden ver estudiantes

@router.get("/", response_model=dict)
def obtener_estudiantes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_docente),  # 👈 DOCENTE + ADMIN
    db: Session = Depends(get_db)
):
    """Obtener lista de estudiantes - DOCENTE + ADMIN"""
    try:
        service = EstudianteService(db)
        estudiantes = service.obtener_todos(skip, limit)
        
        return success_response(
            data=estudiantes,
            message="Estudiantes obtenidos exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id_estudiante}", response_model=dict)
def obtener_estudiante(
    id_estudiante: int,
    current_user = Depends(require_docente),  # 👈 DOCENTE + ADMIN
    db: Session = Depends(get_db)
):
    """Obtener estudiante por ID - DOCENTE + ADMIN"""
    try:
        service = EstudianteService(db)
        estudiante = service.obtener_por_id(id_estudiante)
        
        if not estudiante:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        
        return success_response(
            data=estudiante,
            message="Estudiante obtenido exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ SOLO DOCENTE ACTUALIZAR DATOS ACADÉMICOS ============

@router.put("/{id_estudiante}/academico", response_model=dict)
def actualizar_datos_academicos(
    id_estudiante: int,
    datos: dict,  # notas, observaciones, etc.
    current_user = Depends(require_docente),  # 👈 DOCENTE + ADMIN
    db: Session = Depends(get_db)
):
    """Actualizar información académica del estudiante - DOCENTE + ADMIN"""
    try:
        service = EstudianteService(db)
        estudiante_actualizado = service.actualizar_academico(id_estudiante, datos)
        
        return success_response(
            data=estudiante_actualizado,
            message="Datos académicos actualizados exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ SOLO ADMIN - CRUD ============

@router.post("/", response_model=dict)
def crear_estudiante(
    estudiante_in: EstudianteCreate,
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Crear nuevo estudiante - SOLO ADMIN"""
    try:
        service = EstudianteService(db)
        nuevo_estudiante = service.crear(estudiante_in)
        
        return success_response(
            data=nuevo_estudiante,
            message="Estudiante creado exitosamente",
            status_code=201
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id_estudiante}", response_model=dict)
def actualizar_estudiante(
    id_estudiante: int,
    estudiante_update: EstudianteUpdate,
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Actualizar estudiante - SOLO ADMIN"""
    try:
        service = EstudianteService(db)
        estudiante_actualizado = service.actualizar(id_estudiante, estudiante_update)
        
        return success_response(
            data=estudiante_actualizado,
            message="Estudiante actualizado exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id_estudiante}", response_model=dict)
def eliminar_estudiante(
    id_estudiante: int,
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Eliminar estudiante - SOLO ADMIN"""
    try:
        service = EstudianteService(db)
        service.eliminar(id_estudiante)
        
        return success_response(
            message="Estudiante eliminado exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### 3. ROUTER DE REGISTROS (`registro_router.py`)

**VIGILANTE: Solo crear | ADMIN: CRUD**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import (
    require_admin,
    require_vigilante,
    require_no_vigilante
)
from app.services.registro_service import RegistroService
from app.schemas.registro import RegistroCreate, RegistroResponse
from app.utils.responses import success_response

router = APIRouter(prefix="/registros", tags=["Registros"])


# ============ SOLO VIGILANTE CREAR ============

@router.post("/", response_model=dict)
def crear_registro(
    registro_in: RegistroCreate,
    current_user = Depends(require_vigilante),  # 👈 VIGILANTE + ADMIN
    db: Session = Depends(get_db)
):
    """Crear registro de entrada/salida - VIGILANTE + ADMIN"""
    try:
        service = RegistroService(db)
        nuevo_registro = service.crear(registro_in, current_user["id"])
        
        return success_response(
            data=nuevo_registro,
            message="Registro creado exitosamente",
            status_code=201
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ SOLO VER - DOCENTE + ADMIN (NO VIGILANTE) ============

@router.get("/", response_model=dict)
def obtener_registros(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_no_vigilante),  # 👈 NO VIGILANTE (DOCENTE + ADMIN)
    db: Session = Depends(get_db)
):
    """Obtener lista de registros - DOCENTE + ADMIN (NO VIGILANTE)"""
    try:
        service = RegistroService(db)
        registros = service.obtener_todos(skip, limit)
        
        return success_response(
            data=registros,
            message="Registros obtenidos exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id_registro}", response_model=dict)
def obtener_registro(
    id_registro: int,
    current_user = Depends(require_no_vigilante),  # 👈 NO VIGILANTE
    db: Session = Depends(get_db)
):
    """Obtener registro por ID - DOCENTE + ADMIN (NO VIGILANTE)"""
    try:
        service = RegistroService(db)
        registro = service.obtener_por_id(id_registro)
        
        if not registro:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        
        return success_response(
            data=registro,
            message="Registro obtenido exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ SOLO ADMIN EDITAR/ELIMINAR ============

@router.put("/{id_registro}", response_model=dict)
def actualizar_registro(
    id_registro: int,
    registro_update: dict,
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Actualizar registro - SOLO ADMIN"""
    try:
        service = RegistroService(db)
        registro_actualizado = service.actualizar(id_registro, registro_update)
        
        return success_response(
            data=registro_actualizado,
            message="Registro actualizado exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id_registro}", response_model=dict)
def eliminar_registro(
    id_registro: int,
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Eliminar registro - SOLO ADMIN"""
    try:
        service = RegistroService(db)
        service.eliminar(id_registro)
        
        return success_response(
            message="Registro eliminado exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### 4. ROUTER DE REPORTES (`reporte_router.py`)

**DOCENTE puede ver reportes académicos | ADMIN acceso total**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import (
    require_admin,
    require_docente
)
from app.services.reporte_service import ReporteService
from app.utils.responses import success_response

router = APIRouter(prefix="/reportes", tags=["Reportes"])


# ============ DOCENTE + ADMIN VER REPORTES ============

@router.get("/academicos", response_model=dict)
def obtener_reportes_academicos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_docente),  # 👈 DOCENTE + ADMIN
    db: Session = Depends(get_db)
):
    """Ver reportes académicos - DOCENTE + ADMIN"""
    try:
        service = ReporteService(db)
        reportes = service.obtener_reportes_academicos(skip, limit)
        
        return success_response(
            data=reportes,
            message="Reportes académicos obtenidos exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/asistencia", response_model=dict)
def obtener_reporte_asistencia(
    id_estudiante: int = Query(...),
    current_user = Depends(require_docente),  # 👈 DOCENTE + ADMIN
    db: Session = Depends(get_db)
):
    """Ver reporte de asistencia de un estudiante - DOCENTE + ADMIN"""
    try:
        service = ReporteService(db)
        reporte = service.obtener_asistencia(id_estudiante)
        
        return success_response(
            data=reporte,
            message="Reporte de asistencia obtenido exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ SOLO ADMIN - CREAR/EXPORTAR REPORTES ============

@router.post("/exportar", response_model=dict)
def exportar_reporte(
    filtros: dict,
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Exportar reportes (Excel, PDF) - SOLO ADMIN"""
    try:
        service = ReporteService(db)
        archivo = service.exportar(filtros)
        
        return success_response(
            data=archivo,
            message="Reporte exportado exitosamente"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### 5. ROUTER DE GRADOS (`grado_router.py`)

**Solo ADMIN puede gestionar grados**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import require_admin
from app.services.grado_service import GradoService
from app.schemas.grado import GradoCreate, GradoUpdate, GradoResponse
from app.utils.responses import success_response

router = APIRouter(prefix="/grados", tags=["Grados"])


# ============ SOLO ADMIN ============

@router.get("/", response_model=dict)
def obtener_grados(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Obtener lista de grados - SOLO ADMIN"""
    # ... implementación


@router.post("/", response_model=dict)
def crear_grado(
    grado_in: GradoCreate,
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Crear grado - SOLO ADMIN"""
    # ... implementación


@router.put("/{id_grado}", response_model=dict)
def actualizar_grado(
    id_grado: int,
    grado_update: GradoUpdate,
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Actualizar grado - SOLO ADMIN"""
    # ... implementación


@router.delete("/{id_grado}", response_model=dict)
def eliminar_grado(
    id_grado: int,
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Eliminar grado - SOLO ADMIN"""
    # ... implementación
```

---

### 6. ROUTER DE CONFIGURACIÓN (`config_horario_router.py`)

**Solo ADMIN**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import require_admin
from app.services.config_horario_service import ConfigHorarioService
from app.utils.responses import success_response

router = APIRouter(prefix="/configuracion", tags=["Configuración"])


# ============ SOLO ADMIN ============

@router.get("/horarios", response_model=dict)
def obtener_horarios(
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Obtener configuración de horarios - SOLO ADMIN"""
    # ... implementación


@router.put("/horarios", response_model=dict)
def actualizar_horarios(
    config: dict,
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Actualizar configuración de horarios - SOLO ADMIN"""
    # ... implementación
```

---

### 7. ROUTER DE ROLES (`rol_router.py`)

**Solo ADMIN**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import require_admin
from app.services.rol_service import RolService
from app.schemas.rol import RolCreate, RolUpdate, RolResponse
from app.utils.responses import success_response

router = APIRouter(prefix="/roles", tags=["Roles"])


# ============ SOLO ADMIN ============

@router.get("/", response_model=dict)
def obtener_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(require_admin),  # 👈 SOLO ADMIN
    db: Session = Depends(get_db)
):
    """Obtener lista de roles - SOLO ADMIN"""
    # ... implementación
```

---

## 📊 Matriz de Permisos

| Endpoint | Admin | Docente | Vigilante |
|----------|:-----:|:-------:|:---------:|
| `GET /usuarios` | ✅ | ❌ | ❌ |
| `POST /usuarios` | ✅ | ❌ | ❌ |
| `PUT /usuarios/{id}` | ✅ | ❌ | ❌ |
| `DELETE /usuarios/{id}` | ✅ | ❌ | ❌ |
| `GET /estudiantes` | ✅ | ✅ | ❌ |
| `POST /estudiantes` | ✅ | ❌ | ❌ |
| `PUT /estudiantes/{id}` | ✅ | ❌ | ❌ |
| `PUT /estudiantes/{id}/academico` | ✅ | ✅ | ❌ |
| `DELETE /estudiantes/{id}` | ✅ | ❌ | ❌ |
| `GET /registros` | ✅ | ✅ | ❌ |
| `POST /registros` | ✅ | ❌ | ✅ |
| `PUT /registros/{id}` | ✅ | ❌ | ❌ |
| `DELETE /registros/{id}` | ✅ | ❌ | ❌ |
| `GET /reportes/*` | ✅ | ✅ | ❌ |
| `POST /reportes/exportar` | ✅ | ❌ | ❌ |
| `GET /grados` | ✅ | ❌ | ❌ |
| `POST /grados` | ✅ | ❌ | ❌ |
| `GET /configuracion/*` | ✅ | ❌ | ❌ |
| `PUT /configuracion/*` | ✅ | ❌ | ❌ |
| `GET /roles` | ✅ | ❌ | ❌ |

---

## 🔄 Flujo de Autorización

```
Request HTTP
    ↓
1. get_current_user 
   ├─ Valida JWT
   ├─ Busca usuario en BD
   ├─ Verifica que esté activo
   └─ Retorna: {id, email, nombre, rol, rol_id, permisos}
    ↓
2. Dependencia de Rol (require_admin, require_docente, etc)
   ├─ Verifica current_user.get("rol")
   ├─ Si no coincide → HTTPException 403
   └─ Si coincide → Continúa al endpoint
    ↓
3. Endpoint (si autenticación pasó)
   ├─ Procesa la lógica de negocio
   └─ Retorna respuesta
    ↓
Response HTTP
```

---

## 🛠️ Troubleshooting

### Problema: Error 403 cuando debería ser 200
**Solución**: Verifica que:
1. El rol del usuario en BD sea exactamente: `"admin"`, `"docente"` o `"vigilante"`
2. La dependencia usada es la correcta
3. Revisa logs: muestra `[AUTHZ_ERROR]` con el rol recibido

### Problema: Endpoint sin protección
**Solución**: Asegúrate de agregar la dependencia:
```python
def mi_endpoint(..., current_user = Depends(require_admin), ...):
    # Sin el Depends() NO hay validación
```

### Problema: Vigilante puede ver registros
**Solución**: Usa `require_no_vigilante` en endpoints GET:
```python
@router.get("/")
def obtener_registros(
    current_user = Depends(require_no_vigilante),  # Niega vigilante
    ...
):
```

---

## 📝 Resumen de Mejores Prácticas

✅ **SÍ hacer:**
- Usar `Depends()` en TODOS los endpoints protegidos
- Colocar la dependencia de rol lo primero en los parámetros
- Usar `require_admin` para endpoints sensibles
- Usar `require_docente` para endpoints de docente
- Usar `require_vigilante` para endpoints de vigilante
- Documentar qué roles pueden acceder

❌ **NO hacer:**
- Verificar rol directamente: `if current_user["rol"] == "admin"`  
- Olvidar agregar `Depends()` en endpoints
- Mezclar lógica de autorización con lógica de negocio
- Crear endpoints sin protección

---

## 🚀 Próximos Pasos

1. **Implementar en routers**: Usa esta guía para actualizar todos los routers
2. **Pruebas**: Testear con tokens de diferentes roles
3. **Documentación en Swagger**: Los docstrings de endpoints aparecen automáticamente
4. **Auditoría**: Los logs muestran `[AUTHZ_ERROR]` cuando alguien intenta acceso no autorizado

