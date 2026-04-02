# 🧪 Ejemplos de Test para Autorización basada en Roles

## Configuración Inicial para Testing

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.segurity import create_access_token
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.core.database import get_db

client = TestClient(app)


# ============================================================================
# FIXTURES - Datos de prueba
# ============================================================================

@pytest.fixture
def admin_token(db: Session):
    """Crear token JWT para usuario ADMIN"""
    # Asumir que existe rol admin con id=1
    # Asumir que existe usuario admin con id=1
    token = create_access_token(data={"sub": 1})
    return token


@pytest.fixture
def docente_token(db: Session):
    """Crear token JWT para usuario DOCENTE"""
    # Asumir que existe usuario docente con id=2
    token = create_access_token(data={"sub": 2})
    return token


@pytest.fixture
def vigilante_token(db: Session):
    """Crear token JWT para usuario VIGILANTE"""
    # Asumir que existe usuario vigilante con id=3
    token = create_access_token(data={"sub": 3})
    return token


@pytest.fixture
def sin_token():
    """Sin token (para validar 401)"""
    return None
```

---

## 🔒 Tests para Endpoints de USUARIOS

**Solo ADMIN puede acceder**

```python
# ============================================================================
# TESTS: /usuarios - SOLO ADMIN
# ============================================================================

class TestUsuariosEndpoints:
    """Tests para endpoints de usuarios"""
    
    # ========== ADMIN: Acceso permitido ==========
    
    def test_admin_puede_listar_usuarios(self, admin_token):
        """ADMIN debe poder listar usuarios"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/usuarios/", headers=headers)
        
        assert response.status_code == 200, "ADMIN debe poder listar usuarios"
        data = response.json()
        assert data["status"] == "success"
    
    
    def test_admin_puede_crear_usuario(self, admin_token):
        """ADMIN debe poder crear usuario"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        usuario_data = {
            "nombre": "Juan",
            "apellido1": "Pérez",
            "correo": "juan@example.com",
            "contrasena": "password123",
            "rol_id": 2  # docente
        }
        
        response = client.post("/usuarios/", headers=headers, json=usuario_data)
        
        assert response.status_code == 201, "ADMIN debe poder crear usuario"
        data = response.json()
        assert data["status"] == "success"
    
    
    def test_admin_puede_actualizar_usuario(self, admin_token):
        """ADMIN debe poder actualizar usuario"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        usuario_update = {"nombre": "Juan Updated"}
        
        response = client.put("/usuarios/2", headers=headers, json=usuario_update)
        
        assert response.status_code == 200, "ADMIN debe poder actualizar usuario"
    
    
    def test_admin_puede_eliminar_usuario(self, admin_token):
        """ADMIN debe poder eliminar usuario"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.delete("/usuarios/2", headers=headers)
        
        assert response.status_code == 200, "ADMIN debe poder eliminar usuario"
    
    
    # ========== DOCENTE: Acceso denegado ==========
    
    def test_docente_NO_puede_listar_usuarios(self, docente_token):
        """DOCENTE NO debe poder listar usuarios"""
        headers = {"Authorization": f"Bearer {docente_token}"}
        response = client.get("/usuarios/", headers=headers)
        
        assert response.status_code == 403, "DOCENTE no debe poder listar usuarios"
        data = response.json()
        assert "No autorizado" in data["detail"]
    
    
    def test_docente_NO_puede_crear_usuario(self, docente_token):
        """DOCENTE NO debe poder crear usuario"""
        headers = {"Authorization": f"Bearer {docente_token}"}
        usuario_data = {
            "nombre": "Nuevo",
            "apellido1": "Usuario",
            "correo": "nuevo@example.com",
            "contrasena": "password123",
            "rol_id": 3
        }
        
        response = client.post("/usuarios/", headers=headers, json=usuario_data)
        
        assert response.status_code == 403, "DOCENTE no debe poder crear usuario"
    
    
    def test_docente_NO_puede_eliminar_usuario(self, docente_token):
        """DOCENTE NO debe poder eliminar usuario"""
        headers = {"Authorization": f"Bearer {docente_token}"}
        
        response = client.delete("/usuarios/1", headers=headers)
        
        assert response.status_code == 403, "DOCENTE no debe poder eliminar usuario"
    
    
    # ========== VIGILANTE: Acceso denegado ==========
    
    def test_vigilante_NO_puede_listar_usuarios(self, vigilante_token):
        """VIGILANTE NO debe poder listar usuarios"""
        headers = {"Authorization": f"Bearer {vigilante_token}"}
        response = client.get("/usuarios/", headers=headers)
        
        assert response.status_code == 403, "VIGILANTE no debe poder listar usuarios"
    
    
    def test_vigilante_NO_puede_crear_usuario(self, vigilante_token):
        """VIGILANTE NO debe poder crear usuario"""
        headers = {"Authorization": f"Bearer {vigilante_token}"}
        usuario_data = {
            "nombre": "Test",
            "apellido1": "User",
            "correo": "test@example.com",
            "contrasena": "password123"
        }
        
        response = client.post("/usuarios/", headers=headers, json=usuario_data)
        
        assert response.status_code == 403, "VIGILANTE no debe poder crear usuario"
    
    
    # ========== SIN TOKEN: Acceso denegado ==========
    
    def test_sin_token_NO_puede_acceder(self):
        """Sin token NO debe poder acceder"""
        response = client.get("/usuarios/")
        
        assert response.status_code == 403, "Sin token no debe acceder"
```

---

## 📚 Tests para Endpoints de ESTUDIANTES

**ADMIN: CRUD | DOCENTE: Leer y actualizar académico | VIGILANTE: No accede**

```python
# ============================================================================
# TESTS: /estudiantes - ADMIN + DOCENTE (ver), ADMIN (CRUD)
# ============================================================================

class TestEstudiantesEndpoints:
    """Tests para endpoints de estudiantes"""
    
    # ========== ADMIN: Acceso total ==========
    
    def test_admin_puede_listar_estudiantes(self, admin_token):
        """ADMIN debe poder listar estudiantes"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/estudiantes/", headers=headers)
        
        assert response.status_code == 200
    
    
    def test_admin_puede_crear_estudiante(self, admin_token):
        """ADMIN debe poder crear estudiante"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        estudiante_data = {
            "nombre": "Carlos",
            "apellido1": "González",
            "correo": "carlos@example.com",
            "grado_id": 1
        }
        
        response = client.post("/estudiantes/", headers=headers, json=estudiante_data)
        
        assert response.status_code == 201
    
    
    def test_admin_puede_eliminar_estudiante(self, admin_token):
        """ADMIN debe poder eliminar estudiante"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.delete("/estudiantes/1", headers=headers)
        
        assert response.status_code == 200
    
    
    # ========== DOCENTE: Solo leer y actualizar académico ==========
    
    def test_docente_puede_listar_estudiantes(self, docente_token):
        """DOCENTE debe poder listar estudiantes"""
        headers = {"Authorization": f"Bearer {docente_token}"}
        response = client.get("/estudiantes/", headers=headers)
        
        assert response.status_code == 200
    
    
    def test_docente_puede_actualizar_academico(self, docente_token):
        """DOCENTE debe poder actualizar datos académicos"""
        headers = {"Authorization": f"Bearer {docente_token}"}
        datos_academicos = {
            "nota_final": 4.5,
            "observaciones": "Excelente desempeño"
        }
        
        response = client.put(
            "/estudiantes/1/academico",
            headers=headers,
            json=datos_academicos
        )
        
        assert response.status_code == 200
    
    
    def test_docente_NO_puede_crear_estudiante(self, docente_token):
        """DOCENTE NO debe poder crear estudiante"""
        headers = {"Authorization": f"Bearer {docente_token}"}
        estudiante_data = {"nombre": "Test"}
        
        response = client.post("/estudiantes/", headers=headers, json=estudiante_data)
        
        assert response.status_code == 403
    
    
    def test_docente_NO_puede_eliminar_estudiante(self, docente_token):
        """DOCENTE NO debe poder eliminar estudiante"""
        headers = {"Authorization": f"Bearer {docente_token}"}
        
        response = client.delete("/estudiantes/1", headers=headers)
        
        assert response.status_code == 403
    
    
    # ========== VIGILANTE: Sin acceso ==========
    
    def test_vigilante_NO_puede_ver_estudiantes(self, vigilante_token):
        """VIGILANTE NO debe poder ver estudiantes"""
        headers = {"Authorization": f"Bearer {vigilante_token}"}
        response = client.get("/estudiantes/", headers=headers)
        
        assert response.status_code == 403
```

---

## 📝 Tests para Endpoints de REGISTROS

**ADMIN: CRUD | DOCENTE/ADMIN: Ver | VIGILANTE: Crear**

```python
# ============================================================================
# TESTS: /registros - VIGILANTE (crear), DOCENTE (ver), ADMIN (todo)
# ============================================================================

class TestRegistrosEndpoints:
    """Tests para endpoints de registros"""
    
    # ========== VIGILANTE: Solo crear ==========
    
    def test_vigilante_puede_crear_registro(self, vigilante_token):
        """VIGILANTE debe poder crear registro"""
        headers = {"Authorization": f"Bearer {vigilante_token}"}
        registro_data = {
            "id_estudiante": 1,
            "tipo": "entrada",
            "hora": "08:00"
        }
        
        response = client.post("/registros/", headers=headers, json=registro_data)
        
        assert response.status_code == 201
    
    
    def test_vigilante_NO_puede_ver_registros(self, vigilante_token):
        """VIGILANTE NO debe poder ver registros"""
        headers = {"Authorization": f"Bearer {vigilante_token}"}
        response = client.get("/registros/", headers=headers)
        
        assert response.status_code == 403, "VIGILANTE no debe poder ver registros"
    
    
    def test_vigilante_NO_puede_eliminar_registro(self, vigilante_token):
        """VIGILANTE NO debe poder eliminar registro"""
        headers = {"Authorization": f"Bearer {vigilante_token}"}
        
        response = client.delete("/registros/1", headers=headers)
        
        assert response.status_code == 403
    
    
    # ========== DOCENTE: Solo ver registros ==========
    
    def test_docente_puede_ver_registros(self, docente_token):
        """DOCENTE debe poder ver registros"""
        headers = {"Authorization": f"Bearer {docente_token}"}
        response = client.get("/registros/", headers=headers)
        
        assert response.status_code == 200
    
    
    def test_docente_NO_puede_crear_registro(self, docente_token):
        """DOCENTE NO debe poder crear registro"""
        headers = {"Authorization": f"Bearer {docente_token}"}
        registro_data = {"id_estudiante": 1}
        
        response = client.post("/registros/", headers=headers, json=registro_data)
        
        assert response.status_code == 403
    
    
    # ========== ADMIN: Acceso total ==========
    
    def test_admin_puede_crear_registro(self, admin_token):
        """ADMIN debe poder crear registro"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        registro_data = {"id_estudiante": 1}
        
        response = client.post("/registros/", headers=headers, json=registro_data)
        
        assert response.status_code == 201
    
    
    def test_admin_puede_ver_registros(self, admin_token):
        """ADMIN debe poder ver registros"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/registros/", headers=headers)
        
        assert response.status_code == 200
    
    
    def test_admin_puede_eliminar_registro(self, admin_token):
        """ADMIN debe poder eliminar registro"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.delete("/registros/1", headers=headers)
        
        assert response.status_code == 200
```

---

## 📊 Tests para Endpoints de REPORTES

**ADMIN + DOCENTE: Ver | ADMIN: Exportar | VIGILANTE: Sin acceso**

```python
# ============================================================================
# TESTS: /reportes - DOCENTE (ver), ADMIN (todo)
# ============================================================================

class TestReportesEndpoints:
    """Tests para endpoints de reportes"""
    
    # ========== DOCENTE + ADMIN: Ver reportes ==========
    
    def test_docente_puede_ver_reportes_academicos(self, docente_token):
        """DOCENTE debe poder ver reportes académicos"""
        headers = {"Authorization": f"Bearer {docente_token}"}
        response = client.get("/reportes/academicos", headers=headers)
        
        assert response.status_code == 200
    
    
    def test_admin_puede_ver_reportes_academicos(self, admin_token):
        """ADMIN debe poder ver reportes académicos"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/reportes/academicos", headers=headers)
        
        assert response.status_code == 200
    
    
    # ========== VIGILANTE: Sin acceso ==========
    
    def test_vigilante_NO_puede_ver_reportes(self, vigilante_token):
        """VIGILANTE NO debe poder ver reportes"""
        headers = {"Authorization": f"Bearer {vigilante_token}"}
        response = client.get("/reportes/academicos", headers=headers)
        
        assert response.status_code == 403
    
    
    # ========== ADMIN: Exportar reportes ==========
    
    def test_admin_puede_exportar_reportes(self, admin_token):
        """ADMIN debe poder exportar reportes"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        filtros = {"grado": 1}
        
        response = client.post(
            "/reportes/exportar",
            headers=headers,
            json=filtros
        )
        
        assert response.status_code == 200
    
    
    def test_docente_NO_puede_exportar_reportes(self, docente_token):
        """DOCENTE NO debe poder exportar reportes"""
        headers = {"Authorization": f"Bearer {docente_token}"}
        
        response = client.post(
            "/reportes/exportar",
            headers=headers,
            json={}
        )
        
        assert response.status_code == 403
```

---

## 🚀 Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest app/test/

# Ejecutar tests específicos
pytest app/test/test_authorization.py -v

# Ejecutar con cobertura
pytest app/test/ --cov=app --cov-report=html

# Ejecutar un test específico
pytest app/test/test_authorization.py::TestUsuariosEndpoints::test_admin_puede_listar_usuarios -v
```

---

## 📋 Resumen de Casos de Prueba

### Por Endpoint

| Test | Admin | Docente | Vigilante | Sin Token |
|------|:-----:|:-------:|:---------:|:---------:|
| GET /usuarios | ✅ 200 | ❌ 403 | ❌ 403 | ❌ 403 |
| POST /usuarios | ✅ 201 | ❌ 403 | ❌ 403 | ❌ 403 |
| GET /estudiantes | ✅ 200 | ✅ 200 | ❌ 403 | ❌ 403 |
| POST /estudiantes | ✅ 201 | ❌ 403 | ❌ 403 | ❌ 403 |
| GET /registros | ✅ 200 | ✅ 200 | ❌ 403 | ❌ 403 |
| POST /registros | ✅ 201 | ❌ 403 | ✅ 201 | ❌ 403 |
| GET /reportes | ✅ 200 | ✅ 200 | ❌ 403 | ❌ 403 |
| POST /reportes/exportar | ✅ 200 | ❌ 403 | ❌ 403 | ❌ 403 |

---

## 💡 Validar Respuestas

```python
# Respuesta exitosa (200)
assert response.status_code == 200
assert response.json()["status"] == "success"

# Acceso denegado (403)
assert response.status_code == 403
assert "No autorizado" in response.json()["detail"]

# No autenticado (401)
assert response.status_code == 401
assert "Token" in response.json()["detail"]
```

