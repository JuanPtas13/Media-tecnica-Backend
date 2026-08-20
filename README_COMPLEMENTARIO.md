# Documentación complementaria del backend

Este documento concentra la información técnica que antes estaba distribuida en
varios archivos Markdown. El punto de entrada general del proyecto es
[README.md](README.md).

## Arquitectura

La aplicación está organizada por responsabilidades:

```text
app/
├── core/          Configuración, base de datos y seguridad
├── models/        Entidades SQLAlchemy
├── schemas/       Validación y serialización Pydantic
├── repositories/  Consultas y operaciones de persistencia
├── services/      Reglas de negocio
├── routers/       Rutas HTTP de FastAPI
└── utils/         Respuestas y utilidades compartidas
```

El flujo habitual de una solicitud es:

```text
Cliente -> Router -> Dependencias de seguridad -> Service -> Repository -> BD
```

Las respuestas exitosas usan la estructura estándar del proyecto, con `success`,
`message` y `data`. Los errores se devuelven mediante excepciones HTTP de
FastAPI.

## Recursos disponibles

| Prefijo | Operaciones principales |
| --- | --- |
| `/auth` | Login y logout |
| `/usuarios` | CRUD de usuarios y cambio de contraseña |
| `/estudiantes` | CRUD, búsqueda y filtros por documento, estado y grado |
| `/registros` | Consulta y gestión de registros de asistencia |
| `/grados` | CRUD y consultas de grados |
| `/roles` | CRUD y búsqueda de roles |
| `/config-horarios` | Horarios activos, vigentes y por fecha |
| `/reportes` | Reportes de asistencia y actividad |

La referencia exacta de métodos, parámetros y respuestas se genera en
`/docs` y `/openapi.json` al ejecutar la API.

## Autenticación y roles

`POST /auth/login` es el único acceso público de autenticación. Devuelve un JWT
con el identificador del usuario (`sub`), su rol, el tipo `bearer` y la duración
en segundos. En rutas protegidas se debe enviar:

```http
Authorization: Bearer <access_token>
```

Reglas generales:

| Rol | Permisos |
| --- | --- |
| `ADMIN` | Acceso total y administración de usuarios, roles, grados y horarios |
| `DOCENTE` | Consulta de estudiantes, registros y reportes académicos |
| `VIGILANTE` | Creación de registros de asistencia |

Dependencias de seguridad disponibles en `app/core/segurity.py`:

- `require_admin`: solo `ADMIN`.
- `require_docente`: `DOCENTE` o `ADMIN`.
- `require_vigilante`: `VIGILANTE` o `ADMIN`.
- `require_docente_or_admin`: equivalente a `require_docente`.
- `require_no_vigilante`: permite `DOCENTE` y `ADMIN`.

Un token inválido o ausente produce `401`; un usuario autenticado sin permisos
produce `403`. El logout JWT es stateless: el cliente debe descartar el token.

## Modelo de datos

Las entidades principales son:

- `roles`: roles asignables a los usuarios.
- `usuarios`: credenciales, datos personales, rol y estado.
- `grados`: curso y grupo del estudiante.
- `estudiantes`: datos académicos y código QR único.
- `config_horario`: hora límite, tolerancia y vigencia del horario.
- `registros_ingreso`: fecha, hora, estado (`a_tiempo` o `tarde`), estudiante,
  usuario que registró y configuración aplicada.

Las relaciones completas están representadas en
[docs/diagrams/database_design.md](docs/diagrams/database_design.md).

## Pruebas

Desde la raíz del backend:

```bash
python -m pytest
python -m pytest tests/test_auth_roles.py -v
python -m pytest test_password_simple.py test_password_validation.py -v
```

Las pruebas de autorización deben comprobar, como mínimo:

- `401` sin token o con token inválido.
- `403` cuando el rol no tiene permiso.
- `200` o `201` para un rol autorizado.
- Login correcto, contraseña incorrecta y usuario inactivo.

## Contraseñas

Las contraseñas se almacenan como hashes bcrypt y nunca como texto plano. La
validación limita la contraseña a 72 bytes, que es el límite de bcrypt, y evita
que una entrada demasiado larga provoque un error interno. El login debe
responder con `401` para credenciales inválidas, sin revelar si falló el correo
o la contraseña.

## Seguridad y despliegue

- Define `DATABASE_URL` y `JWT_SECRET_KEY` mediante variables de entorno.
- Usa una clave JWT larga, aleatoria y exclusiva por entorno.
- No subas `.env`, credenciales, tokens ni hashes de prueba.
- En producción, limita `CORS_ORIGINS` al dominio del frontend.
- Mantén `DEBUG=false` y usa HTTPS.
- Revisa los permisos de cada endpoint nuevo con una prueba de rol.

## Diagnóstico rápido

| Síntoma | Revisión |
| --- | --- |
| `401` | Token ausente, expirado, mal formado o credenciales inválidas |
| `403` | El rol del usuario no coincide con la dependencia requerida |
| Error de conexión | `DATABASE_URL`, SSL y disponibilidad de PostgreSQL |
| Error de contraseña | Longitud máxima de 72 bytes y hash bcrypt válido |
| CORS en frontend | Origen del frontend incluido en `CORS_ORIGINS` |

Para comprobar que el servicio responde, visita `/health`. Para inspeccionar la
configuración de las rutas, usa Swagger en `/docs`.
