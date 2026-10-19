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

# Obtener configuración
settings = get_settings()

# Crear tablas en la base de datos (si no existen)
Base.metadata.create_all(bind=engine)

# Inicializar aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API Backend para Control de Asistencia Media Técnica",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Registrar routers
app.include_router(auth_router.router)
app.include_router(estudiante_router.router)
app.include_router(usuario_router.router)
app.include_router(registro_router.router)
app.include_router(grado_router.router)
app.include_router(rol_router.router)
app.include_router(config_horario_router.router)
app.include_router(reporte_router.router)


# Health check
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
    """Endpoint raíz"""
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

























































































































