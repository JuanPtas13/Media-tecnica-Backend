# ⚡ Referencia Rápida - Autorización por Roles

## 🎯 Lo Esencial

### Imports
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

### Uso Básico
```python
@router.get("/endpoint")
def mi_endpoint(current_user = Depends(require_admin)):
    # ✅ Solo ADMIN accede aquí
    pass

@router.get("/endpoint")
def mi_endpoint(current_user = Depends(require_docente)):
    # ✅ DOCENTE + ADMIN acceden
    pass

@router.post("/endpoint")
def mi_endpoint(current_user = Depends(require_vigilante)):
    # ✅ VIGILANTE + ADMIN acceden
    pass
```

---

## 📋 Funciones Disponibles

| Función | Quién accede | Uso |
|---------|-------------|-----|
| `require_admin` | Solo ADMIN | Endpoints críticos |
| `require_docente` | DOCENTE + ADMIN | Endpoints académicos |
| `require_vigilante` | VIGILANTE + ADMIN | Crear registros |
| `require_docente_or_admin` | DOCENTE + ADMIN | Alternativa a require_docente |
| `require_no_vigilante` | DOCENTE + ADMIN | Niega VIGILANTE |
| `permiso_requerido("nombre")` | Basado en permisos | Control granular |

---

## 🛠️ Copy-Paste Ready Examples

### USUARIOS - Solo Admin

<details>
<summary>Click para expandir</summary>

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import require_admin
from app.services.usuario_service import UsuarioService
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.utils.responses import success_response

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/")
def obtener_usuarios(
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Obtener usuarios - SOLO ADMIN"""
    try:
        service = UsuarioService(db)
        usuarios = service.obtener_todos()
        return success_response(data=usuarios)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
def crear_usuario(
    usuario_in: UsuarioCreate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Crear usuario - SOLO ADMIN"""
    try:
        service = UsuarioService(db)
        nuevo = service.crear(usuario_in)
        return success_response(data=nuevo, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id_usuario}")
def actualizar_usuario(
    id_usuario: int,
    usuario_update: UsuarioUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Actualizar usuario - SOLO ADMIN"""
    try:
        service = UsuarioService(db)
        actualizado = service.actualizar(id_usuario, usuario_update)
        return success_response(data=actualizado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id_usuario}")
def eliminar_usuario(
    id_usuario: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Eliminar usuario - SOLO ADMIN"""
    try:
        service = UsuarioService(db)
        service.eliminar(id_usuario)
        return success_response(message="Usuario eliminado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

</details>

---

### ESTUDIANTES - Admin (CRUD) + Docente (Ver)

<details>
<summary>Click para expandir</summary>

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import require_admin, require_docente
from app.services.estudiante_service import EstudianteService
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate
from app.utils.responses import success_response

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])


# ============ DOCENTE + ADMIN VER ============

@router.get("/")
def obtener_estudiantes(
    current_user = Depends(require_docente),  # Docente + Admin
    db: Session = Depends(get_db)
):
    """Obtener estudiantes - DOCENTE + ADMIN"""
    try:
        service = EstudianteService(db)
        estudiantes = service.obtener_todos()
        return success_response(data=estudiantes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id_estudiante}")
def obtener_estudiante(
    id_estudiante: int,
    current_user = Depends(require_docente),  # Docente + Admin
    db: Session = Depends(get_db)
):
    """Obtener estudiante - DOCENTE + ADMIN"""
    try:
        service = EstudianteService(db)
        estudiante = service.obtener_por_id(id_estudiante)
        if not estudiante:
            raise HTTPException(status_code=404, detail="No encontrado")
        return success_response(data=estudiante)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id_estudiante}/academico")
def actualizar_academico(
    id_estudiante: int,
    datos: dict,
    current_user = Depends(require_docente),  # Docente + Admin
    db: Session = Depends(get_db)
):
    """Actualizar datos académicos - DOCENTE + ADMIN"""
    try:
        service = EstudianteService(db)
        actualizado = service.actualizar_academico(id_estudiante, datos)
        return success_response(data=actualizado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ SOLO ADMIN CRUD ============

@router.post("/")
def crear_estudiante(
    estudiante_in: EstudianteCreate,
    current_user = Depends(require_admin),  # Solo Admin
    db: Session = Depends(get_db)
):
    """Crear estudiante - SOLO ADMIN"""
    try:
        service = EstudianteService(db)
        nuevo = service.crear(estudiante_in)
        return success_response(data=nuevo, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id_estudiante}")
def actualizar_estudiante(
    id_estudiante: int,
    estudiante_update: EstudianteUpdate,
    current_user = Depends(require_admin),  # Solo Admin
    db: Session = Depends(get_db)
):
    """Actualizar estudiante - SOLO ADMIN"""
    try:
        service = EstudianteService(db)
        actualizado = service.actualizar(id_estudiante, estudiante_update)
        return success_response(data=actualizado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id_estudiante}")
def eliminar_estudiante(
    id_estudiante: int,
    current_user = Depends(require_admin),  # Solo Admin
    db: Session = Depends(get_db)
):
    """Eliminar estudiante - SOLO ADMIN"""
    try:
        service = EstudianteService(db)
        service.eliminar(id_estudiante)
        return success_response(message="Estudiante eliminado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

</details>

---

### REGISTROS - Vigilante (Crear) + Docente/Admin (Ver)

<details>
<summary>Click para expandir</summary>

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import require_admin, require_vigilante, require_no_vigilante
from app.services.registro_service import RegistroService
from app.schemas.registro import RegistroCreate
from app.utils.responses import success_response

router = APIRouter(prefix="/registros", tags=["Registros"])


# ============ VIGILANTE CREAR ============

@router.post("/")
def crear_registro(
    registro_in: RegistroCreate,
    current_user = Depends(require_vigilante),  # Vigilante + Admin
    db: Session = Depends(get_db)
):
    """Crear registro - VIGILANTE + ADMIN"""
    try:
        service = RegistroService(db)
        nuevo = service.crear(registro_in, current_user["id"])
        return success_response(data=nuevo, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ DOCENTE + ADMIN VER (NO VIGILANTE) ============

@router.get("/")
def obtener_registros(
    current_user = Depends(require_no_vigilante),  # Docente + Admin
    db: Session = Depends(get_db)
):
    """Obtener registros - DOCENTE + ADMIN (NO VIGILANTE)"""
    try:
        service = RegistroService(db)
        registros = service.obtener_todos()
        return success_response(data=registros)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id_registro}")
def obtener_registro(
    id_registro: int,
    current_user = Depends(require_no_vigilante),  # Docente + Admin
    db: Session = Depends(get_db)
):
    """Obtener registro - DOCENTE + ADMIN"""
    try:
        service = RegistroService(db)
        registro = service.obtener_por_id(id_registro)
        if not registro:
            raise HTTPException(status_code=404, detail="No encontrado")
        return success_response(data=registro)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ SOLO ADMIN EDITAR/ELIMINAR ============

@router.put("/{id_registro}")
def actualizar_registro(
    id_registro: int,
    datos: dict,
    current_user = Depends(require_admin),  # Solo Admin
    db: Session = Depends(get_db)
):
    """Actualizar registro - SOLO ADMIN"""
    try:
        service = RegistroService(db)
        actualizado = service.actualizar(id_registro, datos)
        return success_response(data=actualizado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id_registro}")
def eliminar_registro(
    id_registro: int,
    current_user = Depends(require_admin),  # Solo Admin
    db: Session = Depends(get_db)
):
    """Eliminar registro - SOLO ADMIN"""
    try:
        service = RegistroService(db)
        service.eliminar(id_registro)
        return success_response(message="Registro eliminado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

</details>

---

### REPORTES - Docente/Admin (Ver) + Admin (Exportar)

<details>
<summary>Click para expandir</summary>

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import require_admin, require_docente
from app.services.reporte_service import ReporteService
from app.utils.responses import success_response

router = APIRouter(prefix="/reportes", tags=["Reportes"])


# ============ DOCENTE + ADMIN VER ============

@router.get("/academicos")
def obtener_reportes_academicos(
    current_user = Depends(require_docente),  # Docente + Admin
    db: Session = Depends(get_db)
):
    """Ver reportes académicos - DOCENTE + ADMIN"""
    try:
        service = ReporteService(db)
        reportes = service.obtener_reportes_academicos()
        return success_response(data=reportes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/asistencia")
def obtener_reporte_asistencia(
    id_estudiante: int = Query(...),
    current_user = Depends(require_docente),  # Docente + Admin
    db: Session = Depends(get_db)
):
    """Ver reporte de asistencia - DOCENTE + ADMIN"""
    try:
        service = ReporteService(db)
        reporte = service.obtener_asistencia(id_estudiante)
        return success_response(data=reporte)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ SOLO ADMIN EXPORTAR ============

@router.post("/exportar")
def exportar_reporte(
    filtros: dict,
    current_user = Depends(require_admin),  # Solo Admin
    db: Session = Depends(get_db)
):
    """Exportar reportes - SOLO ADMIN"""
    try:
        service = ReporteService(db)
        archivo = service.exportar(filtros)
        return success_response(data=archivo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

</details>

---

## 🧬 Structure Pattern

Todos los endpoints siguen este patrón:

```python
@router.METHOD("/path")
def endpoint_name(
    # 1. Parámetros de entrada
    param: Type,
    
    # 2. Autorización (lo primero después de params)
    current_user = Depends(require_ROLE),
    
    # 3. Base de datos (lo último)
    db: Session = Depends(get_db)
):
    """Descripción - ROLE REQUERIDO"""
    try:
        # Lógica
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## ⚠️ Errores Comunes

### ❌ INCORRECTO
```python
# NO: Verificación manual
@router.get("/endpoint")
def endpoint(current_user = Depends(get_current_user)):
    if current_user["rol"] != "admin":
        raise HTTPException(403, "Not admin")
    # ✗ Duplica lógica, no es reutilizable
```

### ✅ CORRECTO
```python
# SÍ: Usar dependencia
@router.get("/endpoint")
def endpoint(current_user = Depends(require_admin)):
    # ✓ Limpio, reutilizable, centralizado
```

---

## 🔍 Validación Rápida

### Ver qué rol tiene el usuario
```python
@router.get("/whoami")
def whoami(current_user = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "nombre": current_user["nombre"],
        "email": current_user["email"],
        "rol": current_user["rol"],
        "permisos": current_user["permisos"]
    }
```

### Verificar logs
```bash
# En los logs verás:
# ✓ [AUTH_SUCCESS] Usuario autenticado correctamente
# ✓ [AUTHZ_ERROR] Acceso denegado - Rol requerido: ADMIN
```

---

## 🎯 Checklist de Implementación

- [ ] Agregar `Depends(require_admin)` a todos los endpoints `/usuarios`
- [ ] Agregar `Depends(require_docente)` a GET `/estudiantes`
- [ ] Agregar `Depends(require_admin)` a POST/PUT/DELETE `/estudiantes`
- [ ] Agregar `Depends(require_vigilante)` a POST `/registros`
- [ ] Agregar `Depends(require_no_vigilante)` a GET `/registros`
- [ ] Agregar `Depends(require_docente)` a GET `/reportes`
- [ ] Agregar `Depends(require_admin)` a POST `/reportes/exportar`
- [ ] Pruebas con `pytest`
- [ ] Verificar logs en desarrollo

---

## 📱 CURL Examples

```bash
# CON TOKEN ADMIN - Debe funcionar
curl -H "Authorization: Bearer $ADMIN_TOKEN" http://localhost:8000/usuarios/

# CON TOKEN DOCENTE - Debe fallar
curl -H "Authorization: Bearer $DOCENTE_TOKEN" http://localhost:8000/usuarios/
# Respuesta: {"detail":"No autorizado. Se requiere rol: admin"}

# CON TOKEN VIGILANTE - Debe fallar
curl -H "Authorization: Bearer $VIGILANTE_TOKEN" http://localhost:8000/usuarios/
# Respuesta: {"detail":"No autorizado. Se requiere rol: admin"}

# SIN TOKEN - Debe fallar
curl http://localhost:8000/usuarios/
# Respuesta: {"detail":"Token requerido"}
```

