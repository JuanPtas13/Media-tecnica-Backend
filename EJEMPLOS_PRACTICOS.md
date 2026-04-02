"""
EJEMPLOS PRÁCTICOS: Cómo integrar tests, logs y validadores
en tus endpoints existentes.

Estos son ejemplos listos para copiar y pegar en tus routers.
"""

# ============================================
# EJEMPLO 1: Endpoint protegido con validación
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.segurity import get_current_user
from app.utils.auth_validators import diagnosticar_token_problemas
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/usuarios/")
def listar_usuarios(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar usuarios - solo admin y docente.
    
    Con logs y validación de token.
    """
    # Validar que tiene permiso
    if current_user.get("rol") not in ["admin", "docente"]:
        logger.warning(
            f"Acceso denegado a {current_user['email']} "
            f"(rol: {current_user['rol']})"
        )
        raise HTTPException(status_code=403, detail="No autorizado")
    
    # Log de acceso exitoso
    logger.info(
        f"Listado de usuarios | Usuario: {current_user['email']} | "
        f"Rol: {current_user['rol']}"
    )
    
    # Lógica del endpoint
    usuarios = db.query(Usuario).all()
    return {"data": usuarios}


# ============================================
# EJEMPLO 2: Usar dependencias de rol
# ============================================

from app.core.segurity import require_admin, require_docente, require_vigilante


@router.delete("/usuarios/{user_id}")
def eliminar_usuario(
    user_id: int,
    current_user = Depends(require_admin),  # Solo admin
    db: Session = Depends(get_db)
):
    """
    Eliminar usuario - solo ADMIN.
    
    La dependencia require_admin valida automáticamente.
    """
    usuario = db.query(Usuario).get(user_id)
    
    if not usuario:
        logger.warning(
            f"Intento de eliminar usuario inexistente ID: {user_id} | "
            f"Ejecutado por: {current_user['email']}"
        )
        raise HTTPException(status_code=404)
    
    db.delete(usuario)
    db.commit()
    
    logger.info(
        f"Usuario eliminado | ID: {user_id} | "
        f"Eliminado por: {current_user['email']}"
    )
    
    return {"message": "Usuario eliminado"}


@router.post("/registros/")
def crear_registro(
    data: dict,
    current_user = Depends(require_vigilante),  # Vigilante y admin
    db: Session = Depends(get_db)
):
    """
    Crear registro - VIGILANTE y ADMIN.
    
    La dependencia require_vigilante permite a admin también.
    """
    logger.info(
        f"Creando registro | Usuario: {current_user['email']} | "
        f"Rol: {current_user['rol']}"
    )
    
    # Crear registro...
    registro = Registro(**data)
    db.add(registro)
    db.commit()
    
    return {"message": "Registro creado", "id": registro.id}


# ============================================
# EJEMPLO 3: Validación con auth_validators
# ============================================

from app.utils.auth_validators import detectar_permisos_excesivos
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.permiso_repository import PermisoRepository


@router.post("/estudiantes/")
def crear_estudiante(
    data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear estudiante - con validación de seguridad.
    
    Detecta si token ha sido falsificado/modificado.
    """
    # Verificar que los permisos en el token no han sido modificados
    usuario_repo = UsuarioRepository(db)
    usuario_db = usuario_repo.get_by_id(current_user["id"])
    
    if not usuario_db:
        logger.error(
            f"CRITICAL: Usuario en token no existe en BD | "
            f"ID: {current_user['id']}"
        )
        raise HTTPException(status_code=401)
    
    # Obtener permisos reales de BD
    permiso_repo = PermisoRepository(db)
    permisos_db = permiso_repo.obtener_permisos_por_usuario(usuario_db.id_usuario)
    
    # Detectar permisos excesivos (token modificado)
    from app.utils.auth_validators import detectar_permisos_excesivos
    
    excesivos = detectar_permisos_excesivos(
        permisos_db,
        current_user.get("permisos", [])
    )
    
    if excesivos:
        logger.error(
            f"ALERTA SEGURIDAD: Token modificado detectado | "
            f"Usuario: {current_user['email']} | "
            f"Permisos excesivos: {excesivos}"
        )
        raise HTTPException(
            status_code=403,
            detail="Token inválido - Permisos inconsistentes"
        )
    
    # Si pasó validación, proceder
    logger.info(f"Creando estudiante | Usuario: {current_user['email']}")
    
    # Lógica...
    return {"message": "Estudiante creado"}


# ============================================
# EJEMPLO 4: Endpoint público (sin autenticación)
# ============================================

@router.post("/login")
def login(credenciales: dict, db: Session = Depends(get_db)):
    """
    Login - endpoint público.
    
    Con logs de intentos fallidos y éxitos.
    """
    usuario = obtener_usuario_por_email(credenciales["email"], db)
    
    if not usuario:
        logger.warning(
            f"Intento de login con email no existente: {credenciales['email']}"
        )
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    if not usuario.estado:
        logger.warning(
            f"Intento de login con usuario inactivo: {usuario.correo}"
        )
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    
    # Validar contraseña
    from app.core.segurity import verify_password
    
    if not verify_password(credenciales["password"], usuario.contrasena_hash):
        logger.warning(
            f"Intento de login con contraseña incorrecta: {usuario.correo}"
        )
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Login exitoso
    from app.core.segurity import create_access_token
    
    token = create_access_token({"sub": str(usuario.id_usuario)})
    
    logger.info(
        f"Login exitoso | Usuario: {usuario.correo} | "
        f"ID: {usuario.id_usuario} | "
        f"Rol: {usuario.rol.nombre if usuario.rol else 'Sin rol'}"
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id_usuario,
            "email": usuario.correo,
            "nombre": usuario.nombre,
            "rol": usuario.rol.nombre if usuario.rol else None
        }
    }


# ============================================
# EJEMPLO 5: Tests para estos endpoints
# ============================================

"""
# En tests/test_my_endpoints.py

def test_listar_usuarios_sin_token(client: TestClient):
    '''Test: acceso sin token retorna 403'''
    response = client.get("/usuarios/")
    assert response.status_code == 403


def test_eliminar_usuario_sin_admin(client: TestClient, setup_usuarios):
    '''Test: vigilante no puede eliminar usuario'''
    usuario = setup_usuarios["vigilante@test.com"]["usuario"]
    token = create_access_token(data={"sub": str(usuario.id_usuario)})
    
    response = client.delete(
        "/usuarios/5",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403
    assert "No autorizado" in response.json()["detail"]


def test_crear_registro_vigilante(client: TestClient, setup_usuarios):
    '''Test: vigilante puede crear registro'''
    usuario = setup_usuarios["vigilante@test.com"]["usuario"]
    token = create_access_token(data={"sub": str(usuario.id_usuario)})
    
    response = client.post(
        "/registros/",
        json={"tipo": "entrada", "estudiante_id": 1},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200


def test_crear_estudiante_con_token_falsificado(client: TestClient, setup_usuarios):
    '''Test: detecta token con permisos excesivos'''
    usuario = setup_usuarios["vigilante@test.com"]["usuario"]
    
    # Crear token modificado con permisos extra
    from app.core.segurity import create_access_token
    
    fake_token = create_access_token(
        data={
            "sub": str(usuario.id_usuario),
            "permisos": ["admin_access", "delete_user"]  # ⚠️ Permisos falsos
        }
    )
    
    response = client.post(
        "/estudiantes/",
        json={"nombre": "Nuevo"},
        headers={"Authorization": f"Bearer {fake_token}"}
    )
    
    # Debe rechazar porque permisos no coinciden con BD
    assert response.status_code == 403
"""


# ============================================
# EJEMPLO 6: Rutas con múltiples condiciones
# ============================================

@router.put("/estudiantes/{student_id}")
def editar_estudiante(
    student_id: int,
    data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Editar estudiante - admin puede editar cualquiera,
    docente solo puede editar si es su clase.
    """
    
    # Validar rol
    if current_user["rol"] == "vigilante":
        logger.warning(
            f"Vigilante intenta editar estudiante | "
            f"User: {current_user['email']}"
        )
        raise HTTPException(status_code=403, detail="No autorizado")
    
    # Si es docente, validar que sea su clase
    if current_user["rol"] == "docente":
        estudiante = db.query(Estudiante).get(student_id)
        
        if not estudiante:
            raise HTTPException(status_code=404)
        
        # Verificar que el estudiante esté en la clase del docente
        if estudiante.grado.docente_id != current_user["id"]:
            logger.warning(
                f"Docente intenta editar estudiante de otra clase | "
                f"Docente: {current_user['email']} | "
                f"Estudiante clase: {estudiante.grado.docente_id}"
            )
            raise HTTPException(status_code=403, detail="No es tu clase")
    
    # Admin puede editar cualquier estudiante
    logger.info(
        f"Editando estudiante {student_id} | "
        f"Usuario: {current_user['email']} | "
        f"Rol: {current_user['rol']}"
    )
    
    # Editar...
    return {"message": "Estudiante actualizado"}


# ============================================
# EJEMPLO 7: Testing estos endpoints
# ============================================

"""
pytest tests/test_my_endpoints.py -v
pytest tests/test_my_endpoints.py::test_eliminar_usuario_sin_admin -v -s
"""
