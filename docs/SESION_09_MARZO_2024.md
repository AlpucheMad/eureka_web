# Sesión de Trabajo: 9 de Marzo 2024
## Implementación de Modelos y Migraciones en el Proyecto Eureka

Este documento detalla los pasos realizados durante la sesión de trabajo para implementar los modelos de datos y generar las migraciones iniciales en el proyecto Eureka.

### 1. Contexto del Problema

Al intentar generar una migración inicial para los modelos ya definidos en la aplicación, se presentó el siguiente problema:

```bash
flask db migrate -m "Migración inicial con modelos User, Collection, Entry, Tag y EntryTag"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.env] No changes in schema detected.
```

Alembic (el sistema de migraciones que usa Flask-SQLAlchemy) no detectó ningún cambio en el esquema de la base de datos, a pesar de que los modelos estaban correctamente definidos y no existían tablas en la base de datos.

### 2. Verificación de los Modelos de Datos

#### 2.1 Estructura de Modelos

Se verificó que los modelos estaban correctamente definidos en los siguientes archivos:

- `app/models/user.py`: Modelo de usuario
- `app/models/collection.py`: Modelo de colección
- `app/models/entry.py`: Modelo de entrada
- `app/models/tag.py`: Modelos de etiqueta y relación entre etiquetas y entradas
- `app/models/__init__.py`: Importación de todos los modelos

#### 2.2 Importación de Modelos

El archivo `app/models/__init__.py` importaba correctamente todos los modelos:

```python
"""
Módulo de modelos para la aplicación Eureka.

Este paquete contiene todos los modelos de datos utilizados por la aplicación,
implementados con SQLAlchemy ORM.
"""

from app.models.user import User
from app.models.collection import Collection
from app.models.entry import Entry
from app.models.tag import Tag, EntryTag

__all__ = ['User', 'Collection', 'Entry', 'Tag', 'EntryTag']
```

### 3. Verificación de la Base de Datos

Se verificó que la base de datos `eureka_dev` existía y que solo contenía el esquema `public` con la tabla `alembic_version`, pero no tenía las tablas correspondientes a los modelos (`users`, `collections`, `entries`, `tags`, `entry_tags`).

### 4. Resolución del Problema

#### 4.1 Importación Explícita de Modelos en Alembic

El problema se resolvió modificando el archivo `migrations/env.py` para importar explícitamente los modelos, asegurando que Alembic los detectara:

```python
# Importar los modelos explícitamente
from app.models import User, Collection, Entry, Tag, EntryTag
```

Este cambio se realizó justo después de las importaciones iniciales y antes de inicializar el contexto de Alembic.

#### 4.2 Generación de la Migración Inicial

Una vez realizado el cambio, se ejecutó nuevamente el comando para generar la migración:

```bash
flask db migrate -m "Migración inicial con modelos User, Collection, Entry, Tag y EntryTag"
```

Esta vez, Alembic detectó correctamente los modelos y generó un archivo de migración con todas las instrucciones necesarias para crear las tablas en la base de datos.

#### 4.3 Aplicación de la Migración

Finalmente, se aplicó la migración para crear las tablas en la base de datos:

```bash
flask db upgrade
```

El comando se ejecutó correctamente, creando todas las tablas definidas en los modelos.

### 5. Tutorial Paso a Paso

A continuación, se presenta un tutorial detallado para replicar este proceso en cualquier proyecto Flask:

#### Paso 1: Verificar la Definición de Modelos

Asegúrate de que tus modelos estén correctamente definidos usando SQLAlchemy. Cada modelo debe heredar de `db.Model` y tener definidos sus campos, relaciones e índices.

#### Paso 2: Asegurarse de la Importación Correcta en `__init__.py`

Verifica que el archivo `app/models/__init__.py` importe todos los modelos, para que estén disponibles a través del paquete `app.models`:

```python
from app.models.user import User
from app.models.collection import Collection
# ... otros modelos ...

__all__ = ['User', 'Collection', ...]
```

#### Paso 3: Verificar la Configuración de la Base de Datos

Asegúrate de que la configuración de la base de datos sea correcta en `config.py`:

```python
SQLALCHEMY_DATABASE_URI = f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{DB_NAME}"
```

#### Paso 4: Verificar la Existencia de la Base de Datos

Comprueba que la base de datos existe y que tienes permisos para crear tablas en ella.

#### Paso 5: Modificar `migrations/env.py`

Edita el archivo `migrations/env.py` para importar explícitamente los modelos:

```python
import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

# Importar los modelos explícitamente
from app.models import User, Collection, Entry, Tag, EntryTag

# ... resto del archivo ...
```

#### Paso 6: Generar la Migración Inicial

Ejecuta el comando para generar la migración inicial:

```bash
flask db migrate -m "Migración inicial con todos los modelos"
```

#### Paso 7: Revisar el Archivo de Migración Generado

Verifica que el archivo de migración generado (en `migrations/versions/`) contenga todas las instrucciones necesarias para crear las tablas, índices y relaciones.

#### Paso 8: Aplicar la Migración

Ejecuta el comando para aplicar la migración:

```bash
flask db upgrade
```

#### Paso 9: Verificar las Tablas Creadas

Comprueba en tu gestor de base de datos que todas las tablas se hayan creado correctamente.

### 6. Observaciones Importantes

1. **Detección Automática**: Alembic debería detectar automáticamente los modelos definidos en Flask-SQLAlchemy, pero a veces es necesario importarlos explícitamente.

2. **Esquema Public**: En PostgreSQL, el esquema `public` debe existir y ser accesible para el usuario de la base de datos.

3. **Integridad Referencial**: Las migraciones se ejecutan en un orden que respeta la integridad referencial, creando primero las tablas sin dependencias y luego las tablas con claves foráneas.

4. **Versionado**: La tabla `alembic_version` se usa para llevar un registro de las migraciones aplicadas.

### 7. Próximos Pasos

Una vez que los modelos y las tablas están creados, puedes:

1. Implementar seeders para datos iniciales
2. Desarrollar las rutas y vistas para interactuar con los modelos
3. Implementar pruebas para los modelos
4. Implementar la lógica de negocio relacionada con estos modelos

---
Documento creado para el proyecto Eureka
Fecha: 9 de Marzo 2024 