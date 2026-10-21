"""Punto de entrada: configura FastAPI, CORS, rutas y endpoints de estado."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.routers import (
    auth_router, 
    estudiante_router, 
    usuario_router, 
    registro_router, 
    grado_router,
    rol_router,
    config_horario_router,
    reporte_router
)
from app.core.database import Base, engine

# Lee la configuración una vez para reutilizarla en la aplicación y sus rutas.
settings = get_settings()

# Crea tablas nuevas detectadas por SQLAlchemy; no sustituye migraciones existentes.
Base.metadata.create_all(bind=engine)

# Define los metadatos que aparecen en Swagger y OpenAPI.
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API Backend para Control de Asistencia Media Técnica",
)

# Permite que el frontend llame a la API desde los orígenes configurados.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Conecta cada módulo de endpoints a la instancia principal de FastAPI.
app.include_router(auth_router.router)
app.include_router(estudiante_router.router)
app.include_router(usuario_router.router)
app.include_router(registro_router.router)
app.include_router(grado_router.router)
app.include_router(rol_router.router)
app.include_router(config_horario_router.router)
app.include_router(reporte_router.router)


# Endpoint simple para comprobar disponibilidad sin autenticar un usuario.
@app.get("/health", tags=["Health"])
def health_check():
    """Verificar que la API está funcionando"""
    return {
        "success": True,
        "message": "API funcionando correctamente",
        "data": None
    }


@app.get("/", tags=["Root"])
def root():
    """Describe la API y señala los endpoints de documentación y salud."""
    return {
        "success": True,
        "message": "Bienvenido a la API de Control de Asistencia",
        "version": settings.APP_VERSION,
        "endpoints": {
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
























































































































