# Proyecto Media Tecnica

Este es un repositorio del proyecto de media técnica.

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Configuración del Entorno Virtual

Para ejecutar o trabajar en el proyecto, es necesario crear un entorno virtual. Sigue estos pasos:

### 1. Crear el entorno virtual

```
bash
# En Windows
python -m venv venv

# En Linux/Mac
python3 -m venv venv
```

### 2. Activar el entorno virtual

```
bash
# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

### 3. Instalar las dependencias

```
bash
pip install -r requirements.txt
```

## Ejecutar la Aplicación

Una vez configurado el entorno, puedes ejecutar la aplicación de dos formas:

### Opción 1: Directamente con Python

```
bash
python app/app.py
```

### Opción 2: Con Uvicorn

```
bash
uvicorn app.app:app --host 0.0.0.0 --port 8000
```

La aplicación estará disponible en: http://localhost:8000

## Estructura del Proyecto

```
├── app/
│   └── app.py          # Aplicación principal
├── docs/
│   └── diagrams/       # Diagramas del proyecto
├── requirements.txt    # Dependencias del proyecto
└── .gitignore          # Archivos ignorados por Git
```


