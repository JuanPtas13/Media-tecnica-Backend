# Media Técnica Backend

API REST para la gestión de estudiantes, usuarios, roles, registros de
asistencia, horarios y reportes académicos. Está construida con FastAPI,
SQLAlchemy y PostgreSQL, siguiendo una separación por capas entre routers,
servicios, repositorios, modelos y esquemas.

## Requisitos

- Python 3.10 o superior
- PostgreSQL 12 o superior, o una base de datos compatible como Supabase
- `pip`

## Instalación

Desde la carpeta `Media-tecnica-Backend`:

```bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuración

La aplicación carga las variables desde un archivo `.env` en la raíz del
backend. Como mínimo, configura la conexión a PostgreSQL y reemplaza la clave
JWT antes de desplegar:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/media_tecnica
APP_NAME=Media Técnica Backend
APP_VERSION=1.0.0
DEBUG=true
JWT_SECRET_KEY=cambia-esta-clave-por-una-secreta-y-larga
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=["http://localhost:5173"]
CORS_CREDENTIALS=true
CORS_METHODS=["*"]
CORS_HEADERS=["*"]
```

No publiques credenciales de la base de datos ni `JWT_SECRET_KEY`. La conexión
actual se inicializa con `sslmode=require`, por lo que el servidor PostgreSQL
debe aceptar conexiones SSL.

## Ejecución

```bash
 uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000`:

- Documentación interactiva: `http://localhost:8000/docs`
- Especificación OpenAPI: `http://localhost:8000/openapi.json`
- Estado del servicio: `http://localhost:8000/health`

Al iniciar, la aplicación crea las tablas declaradas en los modelos si todavía
no existen.

## Autenticación y autorización

El login es público y devuelve un token JWT:

```http
POST /auth/login
Content-Type: application/json

{
	"email": "usuario@ejemplo.com",
	"contraseña": "tu-contraseña"
}
```

Para los endpoints protegidos, envía el token en cada solicitud:

```http
Authorization: Bearer <access_token>
```

Roles disponibles:

| Rol | Acceso general |
| --- | --- |
| `ADMIN` | Gestión completa del sistema |
| `DOCENTE` | Estudiantes y reportes académicos |
| `VIGILANTE` | Creación de registros de asistencia |

Consulta [README_COMPLEMENTARIO.md](README_COMPLEMENTARIO.md) para conocer las
reglas de autorización, el modelo de datos y las pruebas.

## Recursos de la API

| Prefijo | Funcionalidad |
| --- | --- |
| `/auth` | Inicio y cierre de sesión |
| `/estudiantes` | CRUD, búsqueda y filtros de estudiantes |
| `/usuarios` | Administración de usuarios y contraseñas |
| `/registros` | Registros de entrada, salida y asistencia |
| `/grados` | Administración de grados |
| `/roles` | Administración de roles |
| `/config-horarios` | Configuración de horarios |
| `/reportes` | Reportes de asistencia y actividad |

La lista completa de operaciones, parámetros y respuestas está disponible en
Swagger (`/docs`) y en el esquema OpenAPI (`/openapi.json`).

## Estructura del proyecto

```text
app/
├── core/          Configuración, seguridad y base de datos
├── models/        Modelos SQLAlchemy
├── schemas/       Validación y serialización con Pydantic
├── repositories/  Acceso a datos
├── services/      Lógica de negocio
├── routers/       Endpoints HTTP
├── utils/         Respuestas y utilidades compartidas
└── main.py        Punto de entrada de FastAPI
```

## Pruebas

Ejecuta las pruebas desde la raíz del backend:

```bash
python -m pytest
```

Pruebas disponibles:

- [test_password_simple.py](test_password_simple.py)
- [test_password_validation.py](test_password_validation.py)
- [tests/test_auth_roles.py](tests/test_auth_roles.py)

## Documentación adicional

- [README_COMPLEMENTARIO.md](README_COMPLEMENTARIO.md)
- [docs/diagrams/database_design.md](docs/diagrams/database_design.md)

