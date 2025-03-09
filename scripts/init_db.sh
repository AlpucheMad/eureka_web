#!/bin/bash
# Script para inicializar la base de datos y ejecutar las migraciones iniciales

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directorio del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo -e "${YELLOW}Inicializando la base de datos para Eureka...${NC}"

# Verificar si las migraciones ya están inicializadas
if [ ! -d "migrations/versions" ]; then
    echo -e "${YELLOW}Inicializando migraciones...${NC}"
    python scripts/db_migrate.py init
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error al inicializar las migraciones.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Migraciones inicializadas correctamente.${NC}"
else
    echo -e "${YELLOW}Las migraciones ya están inicializadas.${NC}"
fi

# Generar la migración inicial
echo -e "${YELLOW}Generando migración inicial...${NC}"
python scripts/db_migrate.py migrate -m "Migración inicial con modelos User, Collection, Entry, Tag y EntryTag"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error al generar la migración inicial.${NC}"
    exit 1
fi

echo -e "${GREEN}Migración inicial generada correctamente.${NC}"

# Aplicar la migración
echo -e "${YELLOW}Aplicando migración inicial...${NC}"
python scripts/db_migrate.py upgrade

if [ $? -ne 0 ]; then
    echo -e "${RED}Error al aplicar la migración inicial.${NC}"
    exit 1
fi

echo -e "${GREEN}Migración inicial aplicada correctamente.${NC}"
echo -e "${GREEN}Base de datos inicializada con éxito.${NC}" 