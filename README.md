# 🎉 Media Técnica Backend - Arquitectura Limpia

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?style=flat-square)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.13+-blue?style=flat-square)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue?style=flat-square)](https://www.postgresql.org/)

> API REST profesional para control de asistencia con **arquitectura limpia**, **separación de responsabilidades** y **buenas prácticas**.

---

## 🚀 Inicio Rápido

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar servidor
python -m uvicorn app.main:app --reload

# 3. Acceder a
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
```

---

## 📚 Documentación Completa

- 📖 **[ARQUITECTURA.md](ARQUITECTURA.md)** - Arquitectura detallada
- 📊 **[ESTRUCTURA_VISUAL.md](ESTRUCTURA_VISUAL.md)** - Diagramas y flujos
- ✅ **[CAMBIOS_REALIZADOS.md](CAMBIOS_REALIZADOS.md)** - Todos los cambios
- ⚡ **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** - Tutorial rápido

---

## 🏗️ Estructura

```
app/
├── core/              # Configuración + BD
├── models/            # Modelos SQLAlchemy
├── schemas/           # Validación Pydantic
├── repositories/      # Acceso a datos (CRUD)
├── services/          # Lógica de negocio
├── routers/           # Endpoints HTTP
├── utils/             # Utilidades
└── main.py            # Punto de entrada
```

---

## 📌 Endpoints Principales

```
GET    /estudiantes/              Listar
POST   /estudiantes/              Crear
GET    /estudiantes/{id}          Obtener
PUT    /estudiantes/{id}          Actualizar
DELETE /estudiantes/{id}          Eliminar

GET    /usuarios/
POST   /registros/
```

Ver todos en [ARQUITECTURA.md](ARQUITECTURA.md#-endpoints-configurados)

---

## ✨ Características

✅ Arquitectura limpia (5 capas)  
✅ CRUD completo  
✅ Validación con Pydantic v2  
✅ Response estándar  
✅ Documentación automática (Swagger)  
✅ SQLAlchemy ORM  
✅ 34 endpoints funcionales  

---

## 📝 Requisitos

- Python 3.10+
- PostgreSQL 12+ (o Supabase)
- pip

---

## 🤝 Contribuir

Las mejoras son bienvenidas. Abre un Issue o Pull Request.

---

**¡Tu proyecto está listo para producción! 🚀**

