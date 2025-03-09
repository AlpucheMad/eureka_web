-- Script PostgreSQL completo con validaciones para configurar permisos
-- Este script usa condicionales para evitar errores si los objetos ya existen

-- Crear usuario si no existe
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'eureka_user') THEN
      CREATE USER eureka_user WITH PASSWORD 'Eur3ka_S3cure_P@ss';
   END IF;
END
$$;

-- Dar permisos de creación de base de datos al usuario
ALTER USER eureka_user WITH CREATEDB;

-- Crear bases de datos si no existen
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'eureka_dev') THEN
      CREATE DATABASE eureka_dev;
   END IF;

   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'eureka_test') THEN
      CREATE DATABASE eureka_test;
   END IF;

   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'eureka') THEN
      CREATE DATABASE eureka;
   END IF;
END
$$;

-- Otorgar privilegios sobre las bases de datos
GRANT ALL PRIVILEGES ON DATABASE eureka_dev TO eureka_user;
GRANT ALL PRIVILEGES ON DATABASE eureka_test TO eureka_user;
GRANT ALL PRIVILEGES ON DATABASE eureka TO eureka_user;

-- Conectar a la base de datos eureka_dev y configurar permisos
\c eureka_dev

-- Otorgar privilegios en el esquema public
GRANT ALL PRIVILEGES ON SCHEMA public TO eureka_user;
GRANT CREATE ON SCHEMA public TO eureka_user;

-- Otorgar privilegios en objetos existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO eureka_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO eureka_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO eureka_user;

-- Establecer privilegios para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO eureka_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO eureka_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO eureka_user;

-- Cambiar el propietario del esquema public
ALTER SCHEMA public OWNER TO eureka_user;

-- Conectar a la base de datos eureka_test y configurar permisos
\c eureka_test

-- Otorgar privilegios en el esquema public
GRANT ALL PRIVILEGES ON SCHEMA public TO eureka_user;
GRANT CREATE ON SCHEMA public TO eureka_user;

-- Otorgar privilegios en objetos existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO eureka_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO eureka_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO eureka_user;

-- Establecer privilegios para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO eureka_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO eureka_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO eureka_user;

-- Cambiar el propietario del esquema public
ALTER SCHEMA public OWNER TO eureka_user;

-- Conectar a la base de datos eureka y configurar permisos
\c eureka

-- Otorgar privilegios en el esquema public
GRANT ALL PRIVILEGES ON SCHEMA public TO eureka_user;
GRANT CREATE ON SCHEMA public TO eureka_user;

-- Otorgar privilegios en objetos existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO eureka_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO eureka_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO eureka_user;

-- Establecer privilegios para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO eureka_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO eureka_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO eureka_user;

-- Cambiar el propietario del esquema public
ALTER SCHEMA public OWNER TO eureka_user;

-- Mostrar los permisos del usuario para verificar
\du eureka_user