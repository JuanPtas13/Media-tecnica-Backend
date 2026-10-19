"""
Tests para autenticación JWT y autorización por roles.

Incluye:
- Tests de login (obtención de token)
- Tests de acceso por rol (admin, docente, vigilante)
- Tests de acceso sin token (401)
- Tests con token inválido (401)
- Tests de autorización
"""

import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import base64
import hashlib

from app.main import app
from app.core.database import Base, get_db
from app.core.segurity import create_access_token, hash_password
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.permiso import Permiso
from app.models.rol_permiso import RolPermiso
from app.core.config import get_settings


# Simple hash function for tests (doesn't require bcrypt)
def simple_hash_password_for_tests(password: str) -> str:
    """
    Crear un hash simple para tests (sin bcrypt).
    Para tests solo, no para producción.
    """
    return base64.b64encode(hashlib.sha256(password.encode()).digest()).decode()


def simple_verify_password_for_tests(plain: str, hashed: str) -> bool:
    """
    Verificar hash simple para tests.
    """
    return simple_hash_password_for_tests(plain) == hashed



# =====================================================
# CONFIGURACIÓN DE BD PARA TESTS (SQLite en memoria)
# =====================================================

@pytest.fixture(scope="function")
def test_db():
    """
    Crea una BD en memoria para cada test.
    Automáticamente limpia después de cada test.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal()
    
    # Limpiar
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_db):
    """Cliente de prueba FastAPI"""
    return TestClient(app)


@pytest.fixture
def setup_roles_and_permisos(test_db: Session):
    """
    Crea roles y permisos para los tests.
    
    Roles:
    - admin: todos los permisos
    - docente: ver y crear estudiantes, registros
    - vigilante: solo crear registros
    """
    
    # Crear roles
    rol_admin = Rol(nombre="admin", descripcion="Administrador")
    rol_docente = Rol(nombre="docente", descripcion="Docente")
    rol_vigilante = Rol(nombre="vigilante", descripcion="Vigilante")
    
    test_db.add_all([rol_admin, rol_docente, rol_vigilante])
    test_db.commit()
    test_db.refresh(rol_admin)
    test_db.refresh(rol_docente)
    test_db.refresh(rol_vigilante)
    
    # Crear permisos
    permisos_data = [
        ("ver_usuarios", "Ver listado de usuarios"),
        ("crear_usuario", "Crear un usuario"),
        ("editar_usuario", "Editar un usuario"),
        ("eliminar_usuario", "Eliminar un usuario"),
        ("ver_estudiantes", "Ver estudiantes"),
        ("crear_estudiante", "Crear estudiante"),
        ("editar_estudiante", "Editar estudiante"),
        ("ver_registros", "Ver registros"),
        ("crear_registro", "Crear registro"),
        ("editar_registro", "Editar registro"),
        ("ver_reportes", "Ver reportes"),
    ]
    
    permisos = {}
    for nombre, descripcion in permisos_data:
        p = Permiso(nombre=nombre, descripcion=descripcion)
        test_db.add(p)
        test_db.flush()
        permisos[nombre] = p
    
    test_db.commit()
    
    # Asignar permisos a roles
    # Admin: todos los permisos
    for perm in permisos.values():
        rp = RolPermiso(id_rol=rol_admin.id_roles, id_permiso=perm.id_permiso)
        test_db.add(rp)
    
    # Docente: ver usuarios, estudiantes, crear estudiante, registros, crear registro
    docente_permisos = [
        "ver_usuarios",
        "ver_estudiantes",
        "crear_estudiante",
        "editar_estudiante",
        "ver_registros",
        "crear_registro",
        "ver_reportes",
    ]
    for perm_name in docente_permisos:
        rp = RolPermiso(id_rol=rol_docente.id_roles, id_permiso=permisos[perm_name].id_permiso)
        test_db.add(rp)
    
    # Vigilante: solo crear registros
    for perm_name in ["crear_registro", "ver_registros"]:
        rp = RolPermiso(id_rol=rol_vigilante.id_roles, id_permiso=permisos[perm_name].id_permiso)
        test_db.add(rp)
    
    test_db.commit()
    
    return {
        "admin": rol_admin,
        "docente": rol_docente,
        "vigilante": rol_vigilante,
        "permisos": permisos,
    }


@pytest.fixture
def setup_usuarios(test_db: Session, setup_roles_and_permisos):
    """
    Crea usuarios de prueba con diferentes roles.
    """
    roles = setup_roles_and_permisos
    
    usuarios_data = [
        {
            "email": "admin@test.com",
            "nombre": "Admin",
            "apellido1": "User",
            "rol_id": roles["admin"].id_roles,
            "password": "Password123!",
        },
        {
            "email": "docente@test.com",
            "nombre": "Docente",
            "apellido1": "User",
            "rol_id": roles["docente"].id_roles,
            "password": "Password123!",
        },
        {
            "email": "vigilante@test.com",
            "nombre": "Vigilante",
            "apellido1": "User",
            "rol_id": roles["vigilante"].id_roles,
            "password": "Password123!",
        },
    ]
    
    usuarios = {}
    for data in usuarios_data:
        usuario = Usuario(
            correo=data["email"],
            nombre=data["nombre"],
            apellido1=data["apellido1"],
            contrasena_hash=simple_hash_password_for_tests(data["password"]),  # Use simple hash for tests
            rol_id=data["rol_id"],
            estado=True,
        )
        test_db.add(usuario)
        test_db.flush()
        usuarios[data["email"]] = {
            "usuario": usuario,
            "password": data["password"],
        }
    
    test_db.commit()
    
    return usuarios


# =====================================================
# TESTS DE LOGIN
# =====================================================

class TestLogin:
    """Tests para el endpoint de login"""
    
    def test_login_exitoso(self, client: TestClient, setup_usuarios):
        """
        Test: Login exitoso retorna token y datos del usuario
        """
        response = client.post(
            "/auth/login",
            json={
                "email": "admin@test.com",
                "contraseña": "Password123!",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["access_token"]
        assert data["data"]["token_type"] == "bearer"
        assert data["data"]["usuario"]["email"] == "admin@test.com"
        assert data["data"]["usuario"]["rol"] == "admin"
    
    def test_login_email_incorrecto(self, client: TestClient, setup_usuarios):
        """
        Test: Login con email que no existe retorna 401
        """
        response = client.post(
            "/auth/login",
            json={
                "email": "noexiste@test.com",
                "contraseña": "Password123!",
            }
        )
        
        assert response.status_code == 401
        assert "Email o contraseña incorrectos" in response.json()["detail"]
    
    def test_login_contraseña_incorrecta(self, client: TestClient, setup_usuarios):
        """
        Test: Login con contraseña incorrecta retorna 401
        """
        response = client.post(
            "/auth/login",
            json={
                "email": "admin@test.com",
                "contraseña": "PasswordIncorrecto123!",
            }
        )
        
        assert response.status_code == 401
        assert "Email o contraseña incorrectos" in response.json()["detail"]
    
    def test_login_usuario_inactivo(self, client: TestClient, test_db: Session, setup_roles_and_permisos):
        """
        Test: Login con usuario inactivo retorna 403
        """
        # Crear usuario inactivo
        rol = setup_roles_and_permisos["admin"]
        usuario_inactivo = Usuario(
            correo="inactivo@test.com",
            nombre="Inactivo",
            apellido1="User",
            contrasena_hash=hash_password("Password123!"),
            rol_id=rol.id_rol,
            estado=False,  # Inactivo
        )
        test_db.add(usuario_inactivo)
        test_db.commit()
        
        response = client.post(
            "/auth/login",
            json={
                "email": "inactivo@test.com",
                "contraseña": "Password123!",
            }
        )
        
        assert response.status_code == 403
        assert "Usuario inactivo" in response.json()["detail"]


# =====================================================
# TESTS DE AUTENTICACIÓN (Token valid/invalid)
# =====================================================

class TestAuthentication:
    """Tests para validación de tokens"""
    
    def test_acceso_sin_token(self, client: TestClient):
        """
        Test: Acceso a endpoint protegido sin token retorna 401
        
        La mayoría de endpoints requieren token en header Authorization
        """
        response = client.get("/usuarios/")
        
        assert response.status_code == 403  # HTTPBearer devuelve 403 si no hay credenciales
    
    def test_token_invalido(self, client: TestClient):
        """
        Test: Token malformado retorna 401
        """
        response = client.get(
            "/usuarios/",
            headers={"Authorization": "Bearer token_invalido_xyz"}
        )
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower() or "Token" in response.json()["detail"]
    
    def test_token_expirado(self, client: TestClient, setup_usuarios, test_db: Session):
        """
        Test: Token expirado retorna 401
        """
        usuario = setup_usuarios["admin@test.com"]["usuario"]
        
        # Crear token expirado hace 1 hora
        expired_token = create_access_token(
            data={"sub": str(usuario.id_usuario)},
            expires_delta=timedelta(hours=-1)
        )
        
        response = client.get(
            "/usuarios/",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
        assert "expirado" in response.json()["detail"].lower() or "expired" in response.json()["detail"].lower()
    
    def test_header_authorization_sin_bearer(self, client: TestClient, setup_usuarios):
        """
        Test: Header mal formado (sin 'Bearer') retorna error
        """
        usuario = setup_usuarios["admin@test.com"]["usuario"]
        token = create_access_token(data={"sub": str(usuario.id_usuario)})
        
        # Sin "Bearer"
        response = client.get(
            "/usuarios/",
            headers={"Authorization": token}
        )
        
        assert response.status_code == 403  # HTTPBearer valida el formato


# =====================================================
# TESTS DE ROLES Y AUTORIZACIÓN
# =====================================================

class TestRolesAndAuthorization:
    """Tests para control de roles y permisos"""
    
    def test_admin_puede_acceder_todo(self, client: TestClient, setup_usuarios):
        """
        Test: Admin tiene acceso a todos los endpoints
        """
        usuario = setup_usuarios["admin@test.com"]["usuario"]
        token = create_access_token(data={"sub": str(usuario.id_usuario)})
        
        # Intentar acceder a endpoint de usuarios
        response = client.get(
            "/usuarios/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Debe permitir (200) o al menos no devolver 403 Forbidden
        assert response.status_code in [200, 404, 422]  # No debe ser 403
    
    def test_docente_puede_acceder_estudiantes(self, client: TestClient, setup_usuarios):
        """
        Test: Docente puede ver estudiantes (permiso grant)
        """
        usuario = setup_usuarios["docente@test.com"]["usuario"]
        token = create_access_token(data={"sub": str(usuario.id_usuario)})
        
        response = client.get(
            "/estudiantes/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Debe permitir acceso (200) o no devolver 403
        assert response.status_code in [200, 404, 422]
        assert response.status_code != 403
    
    def test_vigilante_NO_puede_acceder_usuarios(self, client: TestClient, setup_usuarios):
        """
        Test: Vigilante NO puede acceder a usuarios (permiso denegado)
        """
        usuario = setup_usuarios["vigilante@test.com"]["usuario"]
        token = create_access_token(data={"sub": str(usuario.id_usuario)})
        
        response = client.get(
            "/usuarios/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Debe devolver 403 Forbidden
        assert response.status_code == 403
    
    def test_vigilante_puede_crear_registros(self, client: TestClient, setup_usuarios):
        """
        Test: Vigilante puede crear registros (su único permiso)
        """
        usuario = setup_usuarios["vigilante@test.com"]["usuario"]
        token = create_access_token(data={"sub": str(usuario.id_usuario)})
        
        # Nota: Este test puede fallar si no hay datos de dependencias para crear registro
        # pero verifica que el permiso esté asignado correctamente
        response = client.post(
            "/registros/",
            json={
                "id_estudiante": 1,
                "fecha": "2024-04-02",
                "tipo": "entrada",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Vigilante tiene permiso, así que no debe ser 403
        assert response.status_code != 403


# =====================================================
# TESTS DE ERRORES COMUNES
# =====================================================

class TestCommonErrors:
    """Tests para detectar errores comunes en JWT y autorización"""
    
    def test_payload_sin_rol(self, client: TestClient, test_db: Session, setup_roles_and_permisos):
        """
        Test: Token con payload sin "rol" se maneja correctamente
        
        Detecta: payload sin "rol" (si la app lo espera)
        """
        # Crear usuario sin rol
        usuario = Usuario(
            correo="sin_rol@test.com",
            nombre="Sin Rol",
            apellido1="User",
            contrasena_hash=hash_password("Password123!"),
            rol_id=None,  # Sin rol
            estado=True,
        )
        test_db.add(usuario)
        test_db.commit()
        
        # Crear token sin rol en payload
        token = create_access_token(data={"sub": str(usuario.id_usuario)})
        
        response = client.get(
            "/usuarios/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Debe manejarlo (aunque el usuario no tiene rol)
        # No debe fallar con error interno 500
        assert response.status_code != 500
    
    def test_token_con_sub_como_string(self, client: TestClient, setup_usuarios):
        """
        Test: Token con 'sub' como string se convierte correctamente a int
        
        Detecta: tipo incorrecto del campo 'sub'
        """
        usuario = setup_usuarios["admin@test.com"]["usuario"]
        
        # Crear token con 'sub' como string (lo normal)
        token = create_access_token(data={"sub": str(usuario.id_usuario)})
        
        response = client.get(
            "/usuarios/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Debe convertir correctamente
        assert response.status_code != 401
    
    def test_usuario_no_encontrado_en_bd(self, client: TestClient):
        """
        Test: Token válido pero usuario no existe en BD retorna 401
        
        Detecta: usuario eliminado después de generar token
        """
        # Crear token con ID de usuario que no existe
        token = create_access_token(data={"sub": "999999"})
        
        response = client.get(
            "/usuarios/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 401
        assert "no encontrado" in response.json()["detail"].lower() or "usuario" in response.json()["detail"].lower()
    
    def test_swagger_con_token_viejo(self, client: TestClient, setup_usuarios):
        """
        Test: Simula Swagger usando token antiguo que expiró
        
        Detecta: manejo de tokens expirados
        """
        usuario = setup_usuarios["admin@test.com"]["usuario"]
        
        # Token expirado
        old_token = create_access_token(
            data={"sub": str(usuario.id_usuario)},
            expires_delta=timedelta(seconds=-1)
        )
        
        response = client.get(
            "/usuarios/",
            headers={"Authorization": f"Bearer {old_token}"}
        )
        
        assert response.status_code == 401
        assert "expirado" in response.json()["detail"].lower()


# =====================================================
# TESTS DE FLUJO COMPLETO
# =====================================================

class TestFlowComplete:
    """Tests de flujos completos (login -> acceso)"""
    
    def test_flujo_login_y_acceso_admin(self, client: TestClient, setup_usuarios):
        """
        Test: Flujo completo - login -> obtener token -> acceder a recurso
        """
        # 1. Login
        login_response = client.post(
            "/auth/login",
            json={
                "email": "admin@test.com",
                "contraseña": "Password123!",
            }
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["data"]["access_token"]
        
        # 2. Usar token para acceder
        access_response = client.get(
            "/usuarios/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Admin debe tener acceso
        assert access_response.status_code in [200, 404, 422]
        assert access_response.status_code != 403
    
    def test_flujo_login_y_acceso_denegado(self, client: TestClient, setup_usuarios):
        """
        Test: Flujo donde usuario no tiene permisos para recurso
        """
        # 1. Login como vigilante
        login_response = client.post(
            "/auth/login",
            json={
                "email": "vigilante@test.com",
                "contraseña": "Password123!",
            }
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["data"]["access_token"]
        
        # 2. Intentar acceder a usuarios (no tiene permiso)
        access_response = client.get(
            "/usuarios/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Debe devolver 403
        assert access_response.status_code == 403


# =====================================================
# TESTS DE EDGE CASES
# =====================================================

class TestEdgeCases:
    """Tests para casos raros o inesperados"""
    
    def test_token_vacio(self, client: TestClient):
        """
        Test: Header Authorization vacío
        """
        response = client.get(
            "/usuarios/",
            headers={"Authorization": "Bearer "}
        )
        
        assert response.status_code == 401
    
    def test_token_muy_largo(self, client: TestClient):
        """
        Test: Token con contenido inusualmente largo
        """
        fake_token = "x" * 5000
        response = client.get(
            "/usuarios/",
            headers={"Authorization": f"Bearer {fake_token}"}
        )
        
        assert response.status_code == 401
    
    def test_multiples_requests_mismo_token(self, client: TestClient, setup_usuarios):
        """
        Test: Usar el mismo token en múltiples requests (debe funcionar)
        """
        usuario = setup_usuarios["admin@test.com"]["usuario"]
        token = create_access_token(data={"sub": str(usuario.id_usuario)})
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Múltiples requests
        for _ in range(3):
            response = client.get("/usuarios/", headers=headers)
            assert response.status_code in [200, 404, 422]


if __name__ == "__main__":
    # Ejecutar: pytest tests/test_auth_roles.py -v
    pytest.main([__file__, "-v", "-s"])
