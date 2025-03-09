#!/bin/bash
# Script para ejecutar las pruebas de la aplicación Eureka

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directorio del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Configurar entorno de pruebas
export FLASK_ENV=testing
export PYTHONPATH=$PROJECT_DIR

# Verificar si se especificó un patrón de pruebas
if [ $# -eq 0 ]; then
    TEST_PATTERN="tests/"
else
    TEST_PATTERN="$1"
fi

echo -e "${YELLOW}Ejecutando pruebas: ${TEST_PATTERN}${NC}"

# Ejecutar pruebas con pytest
python -m pytest $TEST_PATTERN -v

# Verificar resultado
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Todas las pruebas pasaron correctamente.${NC}"
else
    echo -e "${RED}Algunas pruebas fallaron.${NC}"
    exit 1
fi 