# Migraciones y Pruebas de Modelos en Eureka

Este documento describe el proceso de configuración de migraciones y pruebas para los modelos de datos en la aplicación Eureka.

## Migraciones de Base de Datos

### Configuración Inicial

Las migraciones de base de datos en Eureka se gestionan utilizando Alembic a través de la extensión Flask-Migrate. La configuración se encuentra en:

- `app/__init__.py`: Inicialización de Flask-Migrate
- `migrations/`: Directorio que contiene los scripts de migración
- `scripts/db_migrate.py`: Script para gestionar migraciones desde la línea de comandos

### Comandos de Migración

Para gestionar las migraciones, se pueden utilizar los siguientes comandos:

```bash
# Inicializar migraciones (solo la primera vez)
python scripts/db_migrate.py init

# Generar una nueva migración
python scripts/db_migrate.py migrate -m "Descripción de los cambios"

# Aplicar migraciones pendientes
python scripts/db_migrate.py upgrade

# Revertir la última migración
python scripts/db_migrate.py downgrade --revision <revision>

# Ver el estado actual de las migraciones
python scripts/db_migrate.py current

# Ver el historial de migraciones
python scripts/db_migrate.py history
```

También se proporciona un script para inicializar la base de datos y aplicar la migración inicial:

```bash
./scripts/init_db.sh
```

### Buenas Prácticas para Migraciones

1. Siempre revisar los scripts de migración generados antes de aplicarlos
2. Probar las migraciones en un entorno de desarrollo antes de aplicarlas en producción
3. Mantener un historial claro de migraciones con mensajes descriptivos
4. No modificar migraciones ya aplicadas en entornos compartidos
5. Incluir tanto operaciones de upgrade como downgrade en cada migración

## Pruebas de Modelos

### Estructura de Pruebas

Las pruebas de los modelos se organizan en el directorio `tests/models/` con la siguiente estructura:

- `tests/conftest.py`: Configuración y fixtures comunes para todas las pruebas
- `tests/models/test_user.py`: Pruebas para el modelo User
- `tests/models/test_collection.py`: Pruebas para el modelo Collection
- `tests/models/test_entry.py`: Pruebas para el modelo Entry
- `tests/models/test_tag.py`: Pruebas para los modelos Tag y EntryTag

### Fixtures

Se han definido los siguientes fixtures para facilitar las pruebas:

- `app`: Instancia de la aplicación Flask configurada para pruebas
- `client`: Cliente HTTP para pruebas de vistas
- `db_session`: Sesión de base de datos para pruebas
- `test_user`: Usuario de prueba
- `test_collection`: Colección de prueba
- `test_entry`: Entrada de prueba
- `test_tag`: Etiqueta de prueba

### Ejecución de Pruebas

Para ejecutar las pruebas, se puede utilizar el script `scripts/run_tests.sh`:

```bash
# Ejecutar todas las pruebas
./scripts/run_tests.sh

# Ejecutar pruebas específicas
./scripts/run_tests.sh tests/models/test_user.py
```

O directamente con pytest:

```bash
# Ejecutar todas las pruebas
python -m pytest

# Ejecutar pruebas específicas
python -m pytest tests/models/test_user.py

# Ejecutar pruebas con cobertura
python -m pytest --cov=app
```

### Cobertura de Código

Se ha configurado pytest para generar informes de cobertura de código en varios formatos:

- Terminal: Resumen en la consola
- HTML: Informe detallado en `htmlcov/`
- XML: Informe en formato XML en `coverage.xml`

El umbral mínimo de cobertura se ha establecido en 80%.

## Modelos Implementados

### User

Modelo que representa a los usuarios de la aplicación:

- Atributos: id, username, email, password_hash, is_active, is_verified, created_at, last_login, theme_preference
- Relaciones: collections, entries, tags
- Métodos: verify_password, soft_delete

### Collection

Modelo que representa colecciones de entradas:

- Atributos: id, name, description, user_id, created_at, updated_at, image_path
- Relaciones: user, entries
- Métodos: soft_delete

### Entry

Modelo que representa entradas o ideas:

- Atributos: id, title, content, user_id, collection_id, status, created_at, updated_at
- Relaciones: user, collection, tags
- Métodos: soft_delete, publish, draft, add_tag, remove_tag

### Tag y EntryTag

Modelos que representan etiquetas y la relación muchos a muchos entre entradas y etiquetas:

- Tag: id, name, user_id, created_at, updated_at
- EntryTag: entry_id, tag_id, created_at

## Validaciones Implementadas

- Unicidad de username y email en User
- Unicidad de nombre de etiqueta por usuario en Tag
- Restricción de etiquetas duplicadas por entrada en EntryTag
- Hash seguro de contraseñas con bcrypt
- Soft delete en todos los modelos principales
- Integridad referencial en todas las relaciones 