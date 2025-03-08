-- Create dedicated user for the application
CREATE USER eureka_user WITH PASSWORD 'Eur3ka_S3cure_P@ss';

-- Create databases
CREATE DATABASE eureka_dev;
CREATE DATABASE eureka_test;
CREATE DATABASE eureka;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE eureka_dev TO eureka_user;
GRANT ALL PRIVILEGES ON DATABASE eureka_test TO eureka_user;
GRANT ALL PRIVILEGES ON DATABASE eureka TO eureka_user;

-- Connect to each database to grant schema privileges
\c eureka_dev
GRANT ALL PRIVILEGES ON SCHEMA public TO eureka_user;

\c eureka_test
GRANT ALL PRIVILEGES ON SCHEMA public TO eureka_user;

\c eureka
GRANT ALL PRIVILEGES ON SCHEMA public TO eureka_user;