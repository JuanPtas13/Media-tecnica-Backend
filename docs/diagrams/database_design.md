# Diseño de Base de Datos

## Descripción General

La base de datos fue diseñada para gestionar el control automatizado de ingreso de estudiantes mediante el uso de código QR. 
El sistema registra la hora de llegada, determina si el estudiante llegó a tiempo o tarde y almacena esta información para generar reportes.

Se separaron las entidades de autenticación (usuarios y roles) de las entidades académicas (estudiantes y grados) para mantener una estructura organizada y clara.

También se permite guardar qué usuario realizó un registro y qué configuración de horario fue aplicada en cada ingreso.

---

## Tablas del Sistema

### 1. roles

Almacena los tipos de usuario que pueden acceder al sistema.

Campos principales:

- id_rol (PK)
- nombre
- descripcion
- fecha_creacion
- permisos

Relación:
Un rol puede estar asignado a muchos usuarios.

---

### 2. usuarios

Contiene la información de las personas que pueden iniciar sesión en el sistema.

Campos principales:

- id_usuario (PK)
- nombre
- apellido1
- apellido2
- correo (único)
- contraseña_hash
- rol_id (FK)
- fecha_creacion
- estado

Relación:
Cada usuario pertenece a un rol.
Un usuario puede estar asociado a varios registros de ingreso.

---

### 3. grados

Representa los cursos del colegio (por ejemplo: 6A, 7B).

Campos principales:

- id_grado (PK)
- numero_grado
- grupo
- estado

Relación:
Un grado puede tener muchos estudiantes.

---

### 4. estudiantes

Contiene la información académica de los estudiantes.

Campos principales:

- id_estudiante (PK)
- nombre
- apellido1
- apellido2
- documento
- grado_id (FK)
- codigo_qr (único)
- estado
- fecha_creacion

Relación:
Cada estudiante pertenece a un grado.
Un estudiante puede tener muchos registros de ingreso.

---

### 5. config_horario

Define la hora límite y el tiempo de tolerancia para determinar si un estudiante llegó tarde.

Campos principales:

- id_config (PK)
- hora_inicio_clase
- hora_limite_ingreso
- min_tolerancia
- aplica_desde
- aplica_hasta
- estado

Relación:
Una configuración puede aplicarse a varios registros de ingreso.

---

### 6. registros_ingreso

Registra cada ingreso realizado por los estudiantes.

Campos principales:

- id_registro (PK)
- estudiante_id (FK)
- fecha
- hora
- estado (a_tiempo / tarde)
- min_retraso
- config_id (FK)
- usuario_id (FK)

Relación:
Cada registro pertenece a un estudiante.
Cada registro utiliza una configuración de horario.
Cada registro puede estar asociado a un usuario que lo realizó.
