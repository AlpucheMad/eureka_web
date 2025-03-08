# 🌟 Eureka

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3.3-blue.svg)

Una aplicación web minimalista para capturar y organizar pensamientos e ideas escritas. Eureka te permite crear, organizar y desarrollar tus ideas en un espacio personal digital.

## 📋 Descripción

Eureka es un espacio digital personal donde puedes:
- Capturar rápidamente ideas y pensamientos fugaces
- Organizar tus ideas en colecciones y categorías
- Desarrollar conceptos iniciales en proyectos completos
- Compartir selectivamente tus ideas con colaboradores

## 🛠️ Stack Tecnológico

- **Backend**: Python Flask, SQLAlchemy ORM
- **Frontend**: Tailwind CSS, HTMX
- **Base de datos**: PostgreSQL
- **Autenticación**: Flask-Security-Too
- **Herramientas**: Flask-Migrate, Flask-Mail, WeasyPrint
- **Despliegue**: Docker (recomendado)

## 📂 Estructura del Proyecto

El proyecto sigue una arquitectura MVC:

```
eureka_web/
├── app/                    # Directorio principal de la aplicación
│   ├── models/             # Modelos de datos (SQLAlchemy)
│   ├── views/              # Controladores/Vistas (Blueprints de Flask)
│   ├── templates/          # Plantillas HTML (Jinja2)
│   ├── static/             # Archivos estáticos (CSS, JS, imágenes)
│   ├── services/           # Servicios de lógica de negocio
│   └── utils/              # Utilidades y funciones auxiliares
├── migrations/             # Migraciones de base de datos (Alembic)
├── tests/                  # Pruebas unitarias y de integración
├── config.py               # Configuración de la aplicación
├── requirements.txt        # Dependencias del proyecto
├── wsgi.py                 # Punto de entrada para servidores WSGI
└── .env                    # Variables de entorno (no incluido en Git)
```

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.10+
- PostgreSQL 14+
- Git

### Configuración del Entorno de Desarrollo

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/eureka.git
   cd eureka
   ```

2. Crear y activar un entorno virtual:
   ```bash
   python -m venv eureka-env
   
   # Windows
   eureka-env\Scripts\activate
   
   # Linux/MacOS
   source eureka-env/bin/activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar la base de datos PostgreSQL:
   ```sql
   CREATE USER eureka_user WITH PASSWORD 'Eur3ka_S3cure_P@ss';
   CREATE DATABASE eureka_dev OWNER eureka_user;
   CREATE DATABASE eureka_test OWNER eureka_user;
   ```
   
   **Nota**: Asegúrate de que PostgreSQL esté configurado para usar el puerto 5433.

5. Configurar variables de entorno:
   Copia el archivo `.env.example` a `.env` y ajusta los valores según tu entorno.

6. Inicializar la base de datos:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

7. Ejecutar la aplicación:
   ```bash
   flask run
   ```

## 🧪 Pruebas

Para ejecutar las pruebas:

```bash
pytest
```

## 🔄 Flujo de Desarrollo

Este proyecto sigue el flujo de trabajo Git Flow:

1. `main` - Rama de producción estable
2. `develop` - Rama de desarrollo principal
3. `feature/*` - Ramas de funcionalidades
4. `hotfix/*` - Ramas de correcciones urgentes
5. `release/*` - Ramas de preparación para lanzamientos

### Proceso de Contribución:

1. Crear una rama de funcionalidad desde `develop`
2. Desarrollar y probar
3. Crear un pull request a `develop`
4. Revisión de código
5. Fusionar a `develop`

## 🐳 Despliegue con Docker

1. Construir la imagen:
   ```bash
   docker build -t eureka .
   ```

2. Ejecutar con docker-compose:
   ```bash
   docker-compose up -d
   ```

## 📈 Fases del Proyecto

### MVP (Fase 1)
- Registro y autenticación de usuarios
- Creación básica de notas
- Organización en colecciones simples
- Interfaz responsiva básica

### Fase 2
- Editor avanzado de texto enriquecido
- Etiquetado y categorización
- Búsqueda mejorada
- Exportación a PDF

### Fase 3
- Colaboración en tiempo real
- Integraciones con servicios externos
- Aplicación móvil complementaria
- Funciones de IA para sugerencias y organización

## 👥 Colaboradores

- [Tu Nombre](https://github.com/tu-usuario)

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - vea el archivo [LICENSE](LICENSE) para más detalles.