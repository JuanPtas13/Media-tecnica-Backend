# Media Técnica — Backend

API REST para administrar estudiantes, usuarios, roles, grados, horarios,
registros de asistencia y reportes. El backend está construido con FastAPI,
SQLAlchemy, Pydantic y PostgreSQL.

Esta guía explica desde los requisitos iniciales hasta cómo ejecutar, probar y
diagnosticar la API. Ejecuta los comandos desde la carpeta
`Media-tecnica-Backend`, salvo que se indique otro directorio.

## Índice

1. [Cómo funciona el proyecto](#cómo-funciona-el-proyecto)
2. [Requisitos](#requisitos)
3. [Preparar PostgreSQL](#preparar-postgresql)
4. [Crear el entorno de Python](#crear-el-entorno-de-python)
5. [Configurar las variables](#configurar-las-variables)
6. [Actualizar una base de datos existente](#actualizar-una-base-de-datos-existente)
7. [Iniciar el backend](#iniciar-el-backend)
8. [Iniciar el frontend junto al backend](#iniciar-el-frontend-junto-al-backend)
9. [Comprobar que funciona](#comprobar-que-funciona)
10. [Autenticación y roles](#autenticación-y-roles)
11. [Rutas principales](#rutas-principales)
12. [Ejecutar las pruebas](#ejecutar-las-pruebas)
13. [Solución de problemas](#solución-de-problemas)
14. [Seguridad antes de desplegar](#seguridad-antes-de-desplegar)

## Cómo funciona el proyecto

Una solicitud suele recorrer estas capas:

```text
Frontend
  -> Router FastAPI (recibe la solicitud HTTP)
  -> Dependencias de seguridad (autentican y autorizan)
  -> Service (aplica las reglas de negocio)
  -> Repository (consulta o modifica los datos)
  -> PostgreSQL
```

El backend es la autoridad final para permisos y reglas de asistencia. Ocultar
un botón en el frontend no sustituye la validación del endpoint.

```text
app/
├── core/          Configuración, conexión a base de datos y seguridad
├── models/        Tablas y relaciones de SQLAlchemy
├── repositories/  Consultas a la base de datos
├── routers/       Endpoints HTTP de FastAPI
├── schemas/       Validación de entradas y respuestas con Pydantic
├── services/      Reglas de negocio
├── utils/         Respuestas y utilidades compartidas
└── main.py        Aplicación FastAPI y registro de routers
```

### Funcionamiento de cada carpeta

| Carpeta | Qué contiene y para qué sirve | Cuándo se modifica |
| --- | --- | --- |
| `app/` | Paquete raíz de Python que contiene el código ejecutable de la API. | Al implementar o cambiar el backend. |
| `app/core/` | Ajustes comunes, variables de entorno, conexión/sesiones de SQLAlchemy y autenticación/autorización JWT. | Al cambiar configuración global, base de datos o reglas de autenticación. |
| `app/models/` | Clases SQLAlchemy que describen tablas, columnas, claves y relaciones de la base de datos. | Al cambiar la estructura persistida. Acompaña los cambios de esquema con una migración para bases existentes. |
| `app/schemas/` | Modelos Pydantic para validar lo que entra por la API y definir datos que salen en las respuestas. | Al añadir o modificar campos de solicitudes y respuestas. |
| `app/repositories/` | Consultas a la base de datos: filtros, búsquedas, ordenamiento, inserciones y eliminaciones. No debería contener reglas HTTP. | Al cambiar cómo se leen o guardan datos. |
| `app/services/` | Lógica de negocio que coordina repositorios y aplica reglas como validar horarios, permisos o estados. | Al cambiar el comportamiento de una operación del sistema. |
| `app/routers/` | Rutas/endpoints HTTP, parámetros FastAPI, dependencias de rol, códigos de estado y transformación de errores. | Al publicar una operación nueva o ajustar el contrato HTTP. |
| `app/utils/` | Funciones comunes reutilizadas por distintas capas, como formatos de respuesta, cálculos de tiempo y verificaciones auxiliares. | Al extraer o ajustar una utilidad compartida. |
| `tests/` | Pruebas automáticas para reglas de negocio, autorización y comportamiento de la API. | Cada vez que se corrige o agrega comportamiento. |
| `docs/` | Material de apoyo técnico que no forma parte de las rutas ejecutables. | Al documentar arquitectura, diseño o cambios de base de datos. |
| `docs/diagrams/` | Diagramas visuales y documentación de relaciones entre entidades. | Cuando cambia el modelo o sus relaciones. |
| `docs/migrations/` | Scripts SQL incrementales para actualizar bases que ya tenían tablas antes del cambio. | Cuando un cambio de modelo requiere modificar una base existente. |
| `.venv/` | Paquetes instalados para este proyecto en el equipo local. La crea el desarrollador; no se comparte ni se sube a Git. | La administra Python/pip, no se edita a mano. |

### Funcionamiento de las capas por solicitud

1. **Router:** recibe el método, la ruta, los parámetros y el cuerpo HTTP.
2. **Schema:** FastAPI/Pydantic valida tipos, campos obligatorios y límites de
   la solicitud antes de ejecutar la lógica.
3. **Seguridad (`core/segurity.py`):** valida el token y el rol/permisos
   requeridos por el endpoint.
4. **Service:** aplica las reglas de negocio y coordina el caso de uso.
5. **Repository:** ejecuta consultas SQLAlchemy y devuelve modelos de datos.
6. **Model:** representa la tabla y sus relaciones con otras entidades.
7. **Router/utilidad de respuesta:** transforma el resultado en la respuesta
   JSON estándar del sistema.

Los modelos describen la base de datos; los schemas describen el contrato de la
API. No son intercambiables. Cuando se agrega una columna que debe llegar a una
base existente, actualiza el modelo, el schema apropiado, la lógica que la usa,
las pruebas y una migración SQL.

## Requisitos

- Python 3.10 o superior.
- PostgreSQL 12 o superior, local o administrado (por ejemplo, un proveedor
  compatible con PostgreSQL).
- `pip`, que normalmente se instala junto con Python.
- Para trabajar junto al frontend: Node.js 18 o superior y npm.
- Acceso a una base de datos y credenciales válidas. El backend no trae una
  base de datos ni usuarios de demostración.

Comprueba las herramientas desde PowerShell:

```powershell
python --version
python -m pip --version
```

En algunas instalaciones de Windows el comando de Python puede ser `py`:

```powershell
py --version
```

Si el comando `python` no existe, instala Python desde el sitio oficial y activa
la opción para agregar Python al `PATH`; luego abre una terminal nueva.

## Preparar PostgreSQL

Antes de iniciar FastAPI necesitas una base de datos PostgreSQL alcanzable desde
tu equipo. Puedes usar una instalación local o crear una instancia en tu
proveedor.

1. Crea una base de datos vacía y un usuario con permisos para crear y modificar
   tablas en esa base.
2. Anota el host, el puerto (normalmente `5432`), el nombre de la base, el
   usuario y su contraseña.
3. Conserva esos datos privados. No los pegues en capturas, en el código ni en
   archivos que se vayan a subir a Git.
4. La conexión del proyecto requiere SSL (`sslmode=require`), así que utiliza
   una instancia/proveedor PostgreSQL que admita conexiones SSL.

La URL suele tener esta forma:

```text
postgresql://USUARIO:CONTRASEÑA@HOST:5432/NOMBRE_BASE
```

Sustituye los valores de ejemplo por los datos reales del proveedor. Si la
contraseña incluye caracteres reservados para una URL (por ejemplo `@`, `#`,
`:` o `/`), codifícalos con URL encoding antes de construir `DATABASE_URL`.

## Crear el entorno de Python

Un entorno virtual separa las dependencias de este proyecto de las de otros
proyectos instalados en el equipo.

### Windows PowerShell

Desde la carpeta del backend:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación por la política de ejecución, permite
scripts solo para la terminal actual y vuelve a activar el entorno:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

La opción `-Scope Process` no cambia la política global del equipo. También
puedes omitir la activación y ejecutar directamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### macOS o Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Para salir del entorno virtual cuando termines:

```text
deactivate
```

## Configurar las variables

FastAPI lee la configuración desde un archivo `.env` ubicado en la raíz del
backend. El archivo `.env` contiene secretos y no se debe compartir ni subir a
Git. En este proyecto la configuración local debe crearse manualmente; el
archivo `.env.example` del frontend configura el cliente web, no las
credenciales del backend.

En Windows crea o abre el archivo local:

```powershell
if (-not (Test-Path .env)) { New-Item -ItemType File -Path .env }
notepad .env
```

En macOS/Linux:

```bash
touch .env
nano .env
```

Añade estas variables y sustituye los valores de ejemplo:

```dotenv
DATABASE_URL=postgresql://USUARIO:CONTRASEÑA@HOST:5432/NOMBRE_BASE
JWT_SECRET_KEY=REEMPLAZAR_POR_UN_SECRETO_ALEATORIO_DE_48_CARACTERES_O_MAS
CORS_ORIGINS=["http://localhost:5173"]
DEBUG=true
```

### Qué significa cada variable

| Variable | Obligatoria | Uso |
| --- | --- | --- |
| `DATABASE_URL` | Sí | URL de conexión PostgreSQL. Debe apuntar a una base existente y alcanzable. |
| `JWT_SECRET_KEY` | Sí | Secreto con el que se firman los tokens de acceso. Debe tener al menos 32 caracteres. |
| `CORS_ORIGINS` | Sí | Lista JSON de orígenes web autorizados para llamar a la API. En desarrollo, permite el Vite local. |
| `DEBUG` | No | Activa el modo de depuración y recarga automática al ejecutar `app.main` directamente. Por defecto es `false`. |
| `APP_NAME` | No | Nombre mostrado por la documentación de la API. |
| `APP_VERSION` | No | Versión mostrada por la API. |
| `JWT_ALGORITHM` | No | Algoritmo de firma JWT; por defecto `HS256`. |
| `JWT_EXPIRATION_HOURS` | No | Duración del token en horas; por defecto `24`. |
| `CORS_CREDENTIALS` | No | Permite credenciales en solicitudes CORS; por defecto `true`. |
| `CORS_METHODS` | No | Métodos HTTP habilitados por CORS. |
| `CORS_HEADERS` | No | Encabezados HTTP habilitados por CORS. |

La lista de CORS debe ser JSON válido, con corchetes y comillas dobles. No
incluyas rutas, comodines (`*`), credenciales ni parámetros en los orígenes.
Por ejemplo, `http://localhost:5173` es un origen; `http://localhost:5173/`
con una ruta no es necesario.

Genera un secreto JWT aleatorio localmente. No uses el texto de ejemplo como
secreto real:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copia el resultado como valor de `JWT_SECRET_KEY` en `.env`. No pegues aquí ni
compartas ese resultado. Si una clave real ya fue expuesta, rótala; eliminarla
del archivo actual no la borra del historial de Git.

## Actualizar una base de datos existente

Al arrancar, `app.main` ejecuta `Base.metadata.create_all()`. Esto crea tablas
que todavía no existan, pero **no modifica** tablas ya creadas. Por eso, antes
de usar una base existente con la versión que incorpora la hora de cierre de
asistencia, aplica una sola vez esta migración SQL:

```text
docs/migrations/20261019_add_attendance_cutoff.sql
```

Ejemplo si tienes el cliente `psql` instalado:

```powershell
$env:PGSSLMODE = "require"
psql -h HOST -p 5432 -U USUARIO -d NOMBRE_BASE -f docs/migrations/20261019_add_attendance_cutoff.sql
```

`psql` solicitará la contraseña en la terminal. Usa una copia de seguridad
antes de migrar una base con datos importantes. Sigue también el procedimiento
de migraciones de tu proveedor. No vuelvas a aplicar una migración sin
comprobar primero si ya se ejecutó.

Las configuraciones antiguas quedan con cierre a las 23:59 hasta que un
administrador revise y guarde el horario correspondiente. Después de la
migración, confirma la hora de cierre desde la pantalla de configuración.

## Iniciar el backend

Abre PowerShell en `Media-tecnica-Backend`, activa el entorno virtual y ejecuta:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

En macOS/Linux, con el entorno activo:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Mantén la terminal abierta mientras uses la aplicación. Para detener el servidor
presiona `Ctrl+C`. El modo `--reload` es para desarrollo local; no lo uses como
servidor de producción.

Direcciones locales:

- API: `http://localhost:8000`
- Documentación Swagger: `http://localhost:8000/docs`
- Documentación ReDoc: `http://localhost:8000/redoc`
- Esquema OpenAPI: `http://localhost:8000/openapi.json`
- Estado del servidor: `http://localhost:8000/health`

## Iniciar el frontend junto al backend

El frontend vive en la carpeta hermana `Media-Tecnica-Frontend` y utiliza Vite.
Deja el backend corriendo en una terminal y abre una **segunda terminal**:

```powershell
Set-Location ..\Media-Tecnica-Frontend
npm ci
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
npm run dev
```

Si el archivo `.env` del frontend ya existe, no hace falta reemplazarlo: confirma
que `VITE_API_BASE_URL` apunte al backend local:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

La interfaz quedará en `http://localhost:5173`. Mantén abiertas las dos
terminales. Si cambias la URL o variables del frontend, reinicia Vite para que
las vuelva a cargar.

No pongas secretos en variables `VITE_*`: Vite las incorpora al código que se
envía al navegador. Para producción, `VITE_API_BASE_URL` debe ser una URL HTTPS
del backend; el proyecto rechaza URLs HTTP y hosts locales durante el build de
producción.

## Comprobar que funciona

1. Abre `http://localhost:8000/health`. Debe responder con
   `"success": true`.
2. Abre `http://localhost:8000/docs` para explorar endpoints y probar solicitudes.
3. Abre `http://localhost:5173` para ver el frontend.
4. Inicia sesión con una cuenta existente. El backend no crea usuarios ni
   contraseñas predeterminados al arrancar.
5. Comprueba que el origen del frontend está en `CORS_ORIGINS` si el navegador
   informa un error CORS.

Si todavía no existe un usuario administrador, solicita al responsable de la
base de datos el procedimiento de aprovisionamiento autorizado para este
entorno. No agregues una contraseña inicial real al README ni al código.

## Autenticación y roles

`POST /auth/login` recibe correo y contraseña y devuelve un token JWT. Las rutas
protegidas reciben ese token en el encabezado:

```http
Authorization: Bearer <TOKEN>
```

Roles principales:

| Rol | Acceso general |
| --- | --- |
| `ADMIN` | Administración del sistema y configuración |
| `DOCENTE` | Consulta de registros y reportes académicos |
| `VIGILANTE` | Registro de ingresos de estudiantes |

Un token ausente o inválido normalmente produce `401`. Un usuario autenticado
sin el rol requerido recibe `403`. El logout con JWT es stateless: el cliente
descarta el token y los datos locales.

## Rutas principales

| Prefijo | Funcionalidad |
| --- | --- |
| `/auth` | Inicio y cierre de sesión |
| `/estudiantes` | Búsqueda y administración de estudiantes |
| `/usuarios` | Administración de usuarios |
| `/grados` | Consulta y administración de grados |
| `/roles` | Consulta de roles |
| `/config-horarios` | Horarios activos, vigentes y por fecha |
| `/registros` | Consultar y crear registros de asistencia |
| `/reportes` | Reporte por grado, por estudiante y actividad general |

Para obtener los métodos, parámetros, permisos y formatos exactos, consulta
Swagger en `/docs` o el esquema en `/openapi.json`.

## Ejecutar las pruebas

Desde la carpeta del backend, con el entorno virtual activo:

```powershell
python -m pytest
```

Para ejecutar una prueba específica:

```powershell
python -m pytest tests\test_auth_roles.py -v
python -m pytest tests\test_reporte_service.py -v
```

Las pruebas que importan la configuración necesitan las variables requeridas
por el proyecto. En el entorno de desarrollo local puedes definirlas en `.env`.
Para comprobar una prueba sin conexión al PostgreSQL de desarrollo, configura
variables locales de prueba en la terminal y evita reutilizar credenciales de
producción.

Si `python -m pytest` muestra `No module named pytest`, instala las dependencias
del proyecto con `python -m pip install -r requirements.txt` y vuelve a
intentarlo.

## Solución de problemas

| Síntoma | Qué revisar |
| --- | --- |
| Falta `DATABASE_URL` o `JWT_SECRET_KEY` | Asegúrate de ejecutar desde la raíz del backend y de que `.env` exista con ambas variables. |
| La clave JWT es demasiado corta | Genera un valor aleatorio local de 32 caracteres o más y actualiza `.env`. |
| Error al convertir `CORS_ORIGINS` | Debe ser una lista JSON válida, por ejemplo `["http://localhost:5173"]`. |
| No conecta a PostgreSQL | Comprueba host, puerto, nombre de base, usuario, contraseña, firewall y disponibilidad del servidor. |
| Error SSL de PostgreSQL | El proyecto requiere SSL. Verifica que la instancia admita SSL y que sus datos de conexión sean correctos. |
| `ModuleNotFoundError` al iniciar | Activa `.venv` e instala `requirements.txt` dentro de ese entorno. |
| `uvicorn` no se reconoce | Ejecuta `python -m uvicorn ...` desde el backend con el entorno activado. |
| El navegador muestra un error CORS | Incluye exactamente el origen del frontend (protocolo, host y puerto) en `CORS_ORIGINS`; reinicia el backend. |
| Swagger responde, pero el login falla | Confirma que la cuenta exista, esté activa y tenga una contraseña válida. |
| El frontend muestra error de conexión | Verifica que el backend esté ejecutándose en el puerto configurado por `VITE_API_BASE_URL`. |
| El cambio de esquema no aparece | `create_all()` no actualiza tablas existentes; revisa y ejecuta la migración correspondiente. |

## Seguridad antes de desplegar

- No subas ni compartas `.env`, contraseñas, tokens o claves privadas.
- Utiliza un `JWT_SECRET_KEY` aleatorio y distinto en cada entorno.
- Configura `CORS_ORIGINS` solo con los dominios reales permitidos; no uses `*`.
- Mantén `DEBUG=false` y utiliza HTTPS para el frontend y el backend.
- No ejecutes el servidor de desarrollo con `--reload` en producción.
- Aplica las migraciones antes de lanzar una versión que requiera nuevas
  columnas o tablas.
- Revisa los permisos de los endpoints y las pruebas de autorización antes de
  publicar cambios.

## Documentación relacionada

- [README_COMPLEMENTARIO.md](README_COMPLEMENTARIO.md): arquitectura, roles,
  modelo de datos y comportamiento de la API.
- [docs/diagrams/database_design.md](docs/diagrams/database_design.md):
  diagrama del modelo de datos.
- [Frontend README](../Media-Tecnica-Frontend/README.md): configuración y
  comandos de desarrollo del cliente web.
