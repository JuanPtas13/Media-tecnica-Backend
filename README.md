# Media Técnica Backend

API REST de KronosGate para la gestión educativa. El backend está implementado con FastAPI, SQLAlchemy, Pydantic, PostgreSQL y JWT. Su responsabilidad es autenticar usuarios, validar permisos, administrar estudiantes, grados, usuarios, roles, horarios, registros y reportes, y persistir los datos de forma segura.

## 1. Objetivo del proyecto

KronosGate busca controlar el ingreso a un centro educativo y registrar tardanzas. La parte backend entrega la lógica real del sistema, define los endpoints HTTP y se convierte en la capa que decide qué operaciones están permitidas para cada usuario.

En este repositorio se implementan los siguientes dominios:

- autenticación y sesión basada en JWT
- gestión de usuarios y roles
- gestión de estudiantes
- gestión de grados
- configuración de horarios
- registro de ingreso y asistencia
- reportes por grado, estudiante y rango de fechas

La interfaz puede ocultar funcionalidad, pero el backend es la autoridad final. Si un usuario intenta algo no permitido, el endpoint debe rechazarlo.

## 2. Tecnologías reales utilizadas

La configuración real se observa en `requirements.txt` y `app/core/config.py`.

| Tecnología | Uso real en el proyecto |
| --- | --- |
| Python | lenguaje principal del backend |
| FastAPI | API REST, validación, Swagger / OpenAPI |
| Uvicorn | servidor ASGI para levantar la aplicación |
| SQLAlchemy | ORM para modelar tablas y ejecutar consultas |
| PostgreSQL | base de datos relacional principal |
| psycopg2-binary / psycopg[binary] | drivers PostgreSQL |
| Pydantic v2 | validación de request/response y configuración |
| pydantic-settings | carga de variables de entorno desde `.env` |
| python-jose | generación y validación de JWT |
| bcrypt | hash de contraseñas |
| python-multipart | compatibilidad con formularios multipart |
| email-validator | validación de correos |
| CORS Middleware | permitir llamadas del frontend |

## 3. Estructura real del backend

```text
Media-tecnica-Backend/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── segurity.py
│   ├── models/
│   │   ├── base.py
│   │   ├── config_horario.py
│   │   ├── estudiante.py
│   │   ├── grado.py
│   │   ├── permiso.py
│   │   ├── registro.py
│   │   ├── rol.py
│   │   ├── rol_permiso.py
│   │   └── usuario.py
│   ├── repositories/
│   │   ├── base_repositorie.py
│   │   ├── config_horario_repository.py
│   │   ├── estudiante_repository.py
│   │   ├── grado_repository.py
│   │   ├── permiso_repository.py
│   │   ├── registro_repository.py
│   │   ├── reporte_service.py
│   │   ├── rol_permiso_repository.py
│   │   ├── rol_repository.py
│   │   └── usuario_repository.py
│   ├── routers/
│   │   ├── auth_router.py
│   │   ├── config_horario_router.py
│   │   ├── estudiante_router.py
│   │   ├── grado_router.py
│   │   ├── registro_router.py
│   │   ├── reporte_router.py
│   │   ├── rol_router.py
│   │   └── usuario_router.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── config_horario.py
│   │   ├── estudiante.py
│   │   ├── grado.py
│   │   ├── registro.py
│   │   ├── rol.py
│   │   ├── rol_permiso.py
│   │   └── usuario.py
│   ├── services/
│   │   ├── config_horario_service.py
│   │   ├── estudiante_service.py
│   │   ├── grado_service.py
│   │   ├── permiso_service.py
│   │   ├── registro_service.py
│   │   ├── reporte_service.py
│   │   ├── rol_service.py
│   │   └── usuario_service.py
│   ├── utils/
│   │   ├── auth_validators.py
│   │   ├── permissions.py
│   │   ├── responses.py
│   │   └── time_utils.py
│   ├── __init__.py
│   ├── main.py
│   └── core/
├── tests/
├── .env.example
├── .env
├── README.md
├── requirements.txt
└── docs/
```

### Responsabilidad de cada capa

- `app/core`: configuración global, lectura de `.env`, conexión DB, autenticación y autorización.
- `app/models`: entidades SQLAlchemy que representan tablas.
- `app/repositories`: consultas y operaciones de persistencia.
- `app/services`: reglas de negocio y coordinación entre capas.
- `app/routers`: endpoints HTTP y dependencias FastAPI.
- `app/schemas`: validación de entrada/salida con Pydantic.
- `app/utils`: helpers reutilizables como permisos y respuestas estándar.
- `tests`: pruebas de autenticación, roles, password validation y DB.

## 4. Punto de entrada de la aplicación

La aplicación se levanta desde `app/main.py`.

```python
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API Backend para Control de Asistencia Media Técnica",
)
```

Además, en el mismo archivo se registran los routers e incluye CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)
```

Se incluyen estos routers:

- `auth_router`
- `estudiante_router`
- `usuario_router`
- `registro_router`
- `grado_router`
- `rol_router`
- `config_horario_router`
- `reporte_router`

También se ejecuta esto en arranque:

```python
Base.metadata.create_all(bind=engine)
```

Esto crea tablas si no existen; no reemplaza migraciones formales ni debe tomarse como estrategia definitiva para entornos complejos.

## 5. Configuración y variables de entorno

La configuración se centraliza en `app/core/config.py`.

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str = "Media Técnica Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    CORS_ORIGINS: list[str]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: list[str] = ["Authorization", "Content-Type"]
```

Validaciones reales implementadas:

- `JWT_SECRET_KEY` debe tener al menos 32 caracteres.
- `DATABASE_URL` no puede estar vacía.
- `CORS_ORIGINS` debe ser una lista válida, sin comodines ni rutas.

El archivo `.env.example` contiene el formato esperable:

```env
DATABASE_URL=postgresql://USER:PASS@HOST:5432/DATABASE
APP_NAME=Media Técnica Backend
APP_VERSION=1.0.0
DEBUG=false
JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=["http://localhost:5173"]
CORS_CREDENTIALS=true
CORS_METHODS=["GET","POST","PUT","DELETE","OPTIONS"]
CORS_HEADERS=["Authorization","Content-Type"]
```

## 6. Conexión a la base de datos

La conexión está en `app/core/database.py`.

```python
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
```

Esto muestra que el proyecto usa PostgreSQL con conexión SSL obligatoria. Las rutas usan `Depends(get_db)` para obtener una sesión por solicitud y cerrarla al terminar.

```python
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 7. Modelos principales y relaciones

### `Usuario`

Archivo: `app/models/usuario.py`

Representa el usuario del sistema:

- `id_usuario` PK
- `nombre`, `apellido1`, `apellido2`
- `correo` único
- `contrasena_hash`
- `rol_id` FK a `roles.id_roles`
- `estado`

Relaciones:

- `rol` → `Rol`
- `registros` → `RegistroIngreso`

### `Rol`

Archivo: `app/models/rol.py`

- `id_roles` PK
- `nombre`
- `permisos` (campo textual)
- `descripcion`

Relación con permisos muchos a muchos a través de `rol_permiso`.

### `Permiso` y `RolPermiso`

- `Permiso` define el nombre de una acción autorizable.
- `RolPermiso` crea la relación entre rol y permiso.

### `Grado`

Archivo: `app/models/grado.py`

- `id_grado` PK
- `numero_grado`
- `grupo`
- `estado`

Relación:

- `Grado` tiene muchos `Estudiante`.

### `Estudiante`

Archivo: `app/models/estudiante.py`

- `id_estudiante` PK
- `nombre`, `apellido1`, `apellido2`
- `documento` único
- `grado_id` FK
- `codigo_qr`
- `estado`

Relación:

- `Estudiante` tiene muchos `RegistroIngreso`.

### `ConfigHorario`

Archivo: `app/models/config_horario.py`

Define los horarios de ingreso, tolerancia, cierre y vigencia:

- `hora_inicio_clase`
- `hora_limite_ingreso`
- `hora_cierre_asistencia`
- `min_tolerancia`
- `aplica_desde`, `aplica_hasta`
- `estado`

### `RegistroIngreso`

Archivo: `app/models/registro.py`

- `id` PK
- `estudiante_id` FK
- `usuario_id` FK
- `config_id` FK
- `fecha`, `hora`
- `estado`
- `min_retraso`

```mermaid
erDiagram
    ROL ||--o{ USUARIO : tiene
    ROL ||--o{ ROL_PERMISO : incluye
    PERMISO ||--o{ ROL_PERMISO : participa
    GRADO ||--o{ ESTUDIANTE : contiene
    ESTUDIANTE ||--o{ REGISTRO_INGRESO : genera
    USUARIO ||--o{ REGISTRO_INGRESO : registra
    CONFIG_HORARIO ||--o{ REGISTRO_INGRESO : aplica
```

## 8. Esquemas Pydantic y validación de entrada

Los schemas están en `app/schemas/`.

Ejemplo real en `app/schemas/auth.py`:

```python
class LoginRequest(BaseModel):
    email: EmailStr
    contraseña: str = Field(..., min_length=8, max_length=72)
```

Se valida también el tamaño en bytes UTF-8:

```python
def validar_contrasena_bytes(cls, v):
    bytes_length = len(v.encode('utf-8'))
    if bytes_length > 72:
        raise ValueError("La contraseña no puede exceder 72 bytes en UTF-8")
    return v
```

Esto es importante porque `bcrypt` tiene límite duro de 72 bytes.

## 9. Repositorios, servicios y routers

### Repositorios

Archivos en `app/repositories/`.

Su responsabilidad es acceder a la base de datos. Ejemplo: `UsuarioRepository` busca usuarios por correo o rol.

```python
class UsuarioRepository(BaseRepository[Usuario]):
    def get_by_correo(self, correo: str):
        return self.db.query(self.model).filter(self.model.correo == correo).first()
```

### Servicios

Archivos en `app/services/`.

Aquí se aplican reglas de negocio. Ejemplo: `UsuarioService.crear_usuario` valida correo único, extrae la contraseña, hace hash y luego guarda la entidad.

### Routers

Archivos en `app/routers/`.

Los routers exponen endpoints HTTP. Un ejemplo real es `app/routers/auth_router.py`:

```python
@router.post("/login", response_model=dict, status_code=200)
def login(...):
```

La ruta llama al servicio, valida la credencial y responde con token + datos del usuario.

## 10. Autenticación JWT

La seguridad real está en `app/core/segurity.py`.

### Generación del token

```python
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
```

### Payload real

El login comprende esto:

```python
access_token = create_access_token(
    data={
        "sub": str(usuario.id_usuario),
        "rol": usuario.rol.nombre if usuario.rol else "usuario"
    },
    expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
)
```

El JWT incluye:

- `sub`: ID del usuario
- `rol`: rol del usuario
- `exp`: expiración en UNIX timestamp

### Validación de token

La validación se realiza en `get_current_user()` y `get_current_user_from_token()`.

Casos que se manejan:

- token vacío → `401`
- token expirado → `401`
- firma inválida → `401`
- `sub` incorrecto → `401`
- usuario inexistente → `401`
- usuario inactivo → `403`

```python
payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
```

## 11. Autorización por roles y permisos

La autorización se implementa con dependencias reutilizables en `app/core/segurity.py`.

### Dependencias reales

- `require_admin`
- `require_docente_or_admin`
- `require_vigilante`
- `permiso_requerido("crear_usuario")`

Ejemplo real:

```python
def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    if current_user.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado. Se requiere rol: admin")
    return current_user
```

La utilidad `app/utils/permissions.py` también valida permisos por listas:

```python
def tiene_permiso(user, permiso):
    if user.get("rol") == "admin":
        return True
    return permiso in user.get("permisos", [])
```

Esto muestra que los administradores tienen acceso completo por rol y que los demás usuarios dependen de permisos específicos.

## 12. Contraseñas y hashing

No se guardan contraseñas en texto plano.

```python
def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')
```

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

Se valida que la contraseña no supere 72 bytes UTF-8. Esto es crítico al usar bcrypt.

## 13. Endpoints reales del backend

### 13.1. Autenticación

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| `POST` | `/auth/login` | No | login con email + contraseña |
| `POST` | `/auth/logout` | Sí | cierre de sesión / auditoría |

### 13.2. Usuarios

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| `GET` | `/usuarios/` | `require_admin` | listado |
| `GET` | `/usuarios/activos` | `require_admin` | activos |
| `GET` | `/usuarios/{usuario_id}` | `require_admin` | detalle |
| `POST` | `/usuarios/` | permiso `crear_usuario` | crear usuario |
| `PUT` | `/usuarios/{usuario_id}` | permiso `editar_usuario` | actualizar |
| `PUT` | `/usuarios/{usuario_id}/contrasena` | `require_admin` | cambiar contraseña |
| `DELETE` | `/usuarios/{usuario_id}` | permiso `eliminar_usuario` | eliminar |

### 13.3. Estudiantes

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| `GET` | `/estudiantes/` | `require_docente_or_admin` | listado |
| `GET` | `/estudiantes/buscar` | `require_docente_or_admin` | búsqueda |
| `GET` | `/estudiantes/documento/{documento}` | token válido | búsqueda por documento |
| `GET` | `/estudiantes/activos` | `require_docente_or_admin` | activos |
| `GET` | `/estudiantes/grado/{grado_id}` | `require_docente_or_admin` | estudiantes por grado |
| `GET` | `/estudiantes/{estudiante_id}` | `require_docente_or_admin` | detalle |
| `POST` | `/estudiantes/` | permiso `crear_estudiante` | crear |
| `PUT` | `/estudiantes/{estudiante_id}` | permiso `editar_estudiante` | actualizar |
| `DELETE` | `/estudiantes/{estudiante_id}` | permiso `eliminar_estudiante` | eliminar |

### 13.4. Grados

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| `GET` | `/grados/` | `require_docente_or_admin` | listado |
| `GET` | `/grados/activos` | `require_docente_or_admin` | activos |
| `GET` | `/grados/numero/{numero_grado}` | `require_docente_or_admin` | por número |
| `GET` | `/grados/{grado_id}` | `require_docente_or_admin` | detalle |
| `POST` | `/grados/` | permiso `crear_grado` | crear |
| `PUT` | `/grados/{grado_id}` | permiso `editar_grado` | actualizar |
| `DELETE` | `/grados/{grado_id}` | permiso `eliminar_grado` | eliminar |

### 13.5. Registros de ingreso

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| `GET` | `/registros/` | `require_docente_or_admin` | listado |
| `GET` | `/registros/ultimos` | `require_docente_or_admin` | últimos |
| `GET` | `/registros/estudiante/{estudiante_id}` | `require_docente_or_admin` | historial |
| `GET` | `/registros/usuario/{usuario_id}` | `require_admin` | auditoría |
| `GET` | `/registros/fecha/{fecha}` | `require_docente_or_admin` | filtro por fecha |
| `GET` | `/registros/estado/{estado}` | `require_docente_or_admin` | filtro por estado |
| `GET` | `/registros/{registro_id}` | `require_docente_or_admin` | detalle |
| `POST` | `/registros/` | `require_vigilante` | registrar ingreso |
| `PUT` | `/registros/{registro_id}` | permiso `editar_registro` | actualizar |
| `DELETE` | `/registros/{registro_id}` | permiso `eliminar_registro` | eliminar |

### 13.6. Configuración horaria

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| `GET` | `/config-horarios/` | `require_docente_or_admin` | listado |
| `GET` | `/config-horarios/activos` | `require_docente_or_admin` | activos |
| `GET` | `/config-horarios/vigente` | token válido | vigente |
| `GET` | `/config-horarios/fecha/{fecha}` | `require_docente_or_admin` | por fecha |
| `GET` | `/config-horarios/{config_id}` | `require_docente_or_admin` | detalle |
| `POST` | `/config-horarios/` | permiso `crear_config_horario` | crear |
| `PUT` | `/config-horarios/{config_id}` | permiso `editar_config_horario` | actualizar |
| `DELETE` | `/config-horarios/{config_id}` | permiso `eliminar_config_horario` | eliminar |

### 13.7. Roles

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| `GET` | `/roles/` | `require_admin` | listado |
| `GET` | `/roles/nombre/{nombre}` | `require_admin` | búsqueda por nombre |
| `GET` | `/roles/buscar` | `require_admin` | búsqueda |
| `GET` | `/roles/{rol_id}` | `require_admin` | detalle |

### 13.8. Reportes

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| `GET` | `/reportes/asistencia/grado/{grado_id}` | `require_docente_or_admin` | reporte por grado |
| `GET` | `/reportes/asistencia/estudiante/{estudiante_id}` | `require_docente_or_admin` | reporte por estudiante |
| `GET` | `/reportes/actividad` | `require_docente_or_admin` | actividad por rango |

## 14. Flujo de una solicitud real

```mermaid
flowchart LR
    A[Cliente HTTP] --> B[Router FastAPI]
    B --> C[Schema Pydantic]
    C --> D[Dependencias de seguridad]
    D --> E[Servicio]
    E --> F[Repositorio]
    F --> G[(PostgreSQL)]
    G --> F
    F --> E
    E --> H[Respuesta JSON]
    H --> I[HTTP 200/201/400/401/403/404/422/500]
```

Ejemplo de login:

1. El cliente envía `POST /auth/login` con email y contraseña.
2. FastAPI valida el schema `LoginRequest`.
3. `UsuarioService` busca el usuario por correo.
4. `verify_password` compara el hash contra la contraseña enviada.
5. Si es correcta, se genera un JWT con `sub` y `rol`.
6. El backend responde con `access_token`, `token_type`, `expires_in` y `user`.
7. El cliente guarda el token y lo usa en futuras llamadas autenticadas.

## 15. Manejo de errores y códigos HTTP

Códigos reales que aparecen en la implementación:

- `200 OK` para respuestas exitosas.
- `201 Created` en creación de registros.
- `400 Bad Request` para validaciones de negocio o fechas inválidas.
- `401 Unauthorized` para token faltante, inválido o expirado.
- `403 Forbidden` para acceso no autorizado.
- `404 Not Found` cuando no existe un registro.
- `422 Unprocessable Entity` cuando el schema rechaza datos.
- `500 Internal Server Error` para fallos inesperados.

En los routers se usan `HTTPException` con `detail` para devolver mensajes específicos.

## 16. Pruebas reales del proyecto

La carpeta `tests/` incluye varias pruebas:

- `test_auth_roles.py`
- `test_db.py`
- `test_estudiante_delete.py`
- `test_password_simple.py`
- `test_password_validation.py`
- `test_query.py`
- `test_registro_schema.py`
- `test_reporte_service.py`

Se ejecutan con pytest.

```powershell
cd "C:\Users\PC\OneDrive\Escritorio\Media tecnica\Media-tecnica-Backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pytest -q
```

## 17. Cómo ejecutar el backend

### Requisitos

- Python 3.10+
- PostgreSQL accesible desde el equipo
- `.env` correcto con los valores reales del entorno

### Pasos

```powershell
cd "C:\Users\PC\OneDrive\Escritorio\Media tecnica\Media-tecnica-Backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
copy .env.example .env
```

Editar `.env` con la URL real de la base de datos y secret key válida.

Luego arrancar:

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger queda disponible en:

- http://localhost:8000/docs
- http://localhost:8000/openapi.json

## 18. Seguridad y limitaciones reales

El backend implementa autenticación con JWT, validación por roles y contraseñas hasheadas con bcrypt. Sin embargo, hay aspectos que conviene tener presentes:

- la sesión es stateless; no hay blacklist real de tokens implementada en la base de datos.
- la autenticación se basa en un token en Authorization con Bearer.
- CORS está limitado por orígenes declarados en configuración.
- el arranque usa `create_all()`, que facilita desarrollo, pero no reemplaza migraciones en producción.

No se debe afirmar que hay protección absoluta contra todas las amenazas sin evidencia en código; lo que sí está comprobado aquí es la validación de JWT, control de permisos, hash bcrypt y restricciones de entrada.

## 19. Preguntas técnicas para la sustentación

### Básicas

1. ¿Qué es FastAPI y qué hace en este proyecto?  
   Es el framework web del backend. Define rutas, validación de solicitudes, Swagger/OpenAPI y dependencias.

2. ¿Qué es SQLAlchemy?  
   Es el ORM que conecta las clases Python con la base de datos PostgreSQL.

3. ¿Qué diferencia hay entre `model` y `schema`?  
   El modelo representa la tabla; el schema representa la entrada/salida HTTP y valida datos.

4. ¿Qué hace `get_db`?  
   Crea una sesión por petición y la cierra al finalizar.

5. ¿Qué es JWT?  
   Un token firmado que permite autenticar al usuario sin guardar sesión en servidor.

### Seguridad

6. ¿Qué se guarda en el payload del JWT?  
   `sub`, `rol` y `exp` en la implementación real.

7. ¿Cómo se valida un token?  
   Con `jwt.decode` usando la clave secreta y el algoritmo configurado.

8. ¿Cómo se comprueba si el usuario tiene permisos?  
   Con dependencias de seguridad y funciones de permisos (`tiene_permiso`, `permiso_requerido`, etc.).

9. ¿Qué diferencia hay entre autenticación y autorización?  
   Autenticación identifica quién es; autorización decide qué puede hacer.

10. ¿Qué hace bcrypt en el proyecto?  
   Hashea y verifica contraseñas de usuarios.

### Arquitectura

11. ¿Qué papel cumple cada capa del backend?  
   Router expone HTTP, service aplica negocio, repository persiste, modelotabla, schema valida.

12. ¿Qué pasa si el frontend intenta llamar un endpoint sin token?  
   El backend responde `401` con `WWW-Authenticate: Bearer`.

13. ¿Qué pasa si el token expira?  
   La decodificación lanza `ExpiredSignatureError` y el backend responde `401`.

14. ¿Qué ocurre si un usuario intenta acceder a un recurso sin el rol correcto?  
   Se genera `HTTPException(403, detail=...)` en la dependencia de autorización.

15. ¿Qué es CORS en este proyecto?  
   Es la política que permite que el frontend del dominio configurado llame a la API.

### Base de datos

16. ¿Qué relación existe entre `Usuario` y `Rol`?  
   Un usuario tiene un rol; un rol puede tener varios usuarios.

17. ¿Qué relación existe entre `Grado` y `Estudiante`?  
   Un grado contiene varios estudiantes.

18. ¿Qué hace la tabla `rol_permiso`?  
   Relaciona roles con permisos.

19. ¿Qué representa `config_horario`?  
   Define los tiempos de inicio, tolerancia y cierre de asistencia.

20. ¿Qué representa `registro_ingreso`?  
   Cada registro refleja el ingreso, hora, fecha, retraso y estado asociado a un estudiante.

## 20. Glosario

- API: conjunto de endpoints que exponen la funcionalidad del sistema.
- REST: estilo de arquitectura basado en recursos y HTTP.
- JWT: token firmado para autenticación.
- Claim: campo dentro de un JWT, por ejemplo `sub` o `exp`.
- ORM: mapeo de objetos a tablas DB.
- SQLAlchemy: ORM principal del proyecto.
- Pydantic: validación de datos para Python.
- Router: capa de endpoints HTTP.
- Service: lógica de negocio.
- Repository: acceso a persistencia.
- Model: clase que representa una tabla SQLAlchemy.
- Schema: estructura de validación de request/response.
- CORS: control de acceso entre orígenes distintos.
- Hashing: transformación irreversible para proteger passwords.
- PK: clave primaria.
- FK: clave foránea.
- HTTPException: error controlado en FastAPI.

## 21. Conclusión

El backend de KronosGate es una API REST organizada por capas: routers, servicios, repositorios, modelos y esquemas. La seguridad real se valida en FastAPI mediante JWT, dependencias de autorización y hash de contraseñas con bcrypt. La persistencia se gestiona con SQLAlchemy y PostgreSQL, lo que permite un sistema claro y extensible para registrar asistencia escolar y controlar permisos por rol.

Este README refleja la implementación real observada en el código del repositorio y evita describir funcionalidad no respaldada por archivos del proyecto.
