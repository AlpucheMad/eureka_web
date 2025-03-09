#!/usr/bin/env python
"""
Script para inicializar y ejecutar migraciones de base de datos para Eureka.

Este script proporciona una interfaz de línea de comandos para gestionar
las migraciones de base de datos utilizando Flask-Migrate/Alembic.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Añadir el directorio raíz del proyecto al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from app import create_app, db

def parse_args():
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description='Gestionar migraciones de base de datos para Eureka')
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando init
    init_parser = subparsers.add_parser('init', help='Inicializar migraciones')
    
    # Comando migrate
    migrate_parser = subparsers.add_parser('migrate', help='Generar una nueva migración')
    migrate_parser.add_argument('-m', '--message', required=True, help='Mensaje descriptivo para la migración')
    
    # Comando upgrade
    upgrade_parser = subparsers.add_parser('upgrade', help='Aplicar migraciones pendientes')
    upgrade_parser.add_argument('--revision', default='head', help='Revisión a la que actualizar (por defecto: head)')
    
    # Comando downgrade
    downgrade_parser = subparsers.add_parser('downgrade', help='Revertir migraciones')
    downgrade_parser.add_argument('--revision', required=True, help='Revisión a la que revertir')
    
    # Comando history
    subparsers.add_parser('history', help='Mostrar historial de migraciones')
    
    # Comando current
    subparsers.add_parser('current', help='Mostrar revisión actual')
    
    return parser.parse_args()

def run_flask_command(command):
    """Ejecuta un comando de Flask."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error al ejecutar el comando: {command}")
        print(f"Salida de error: {result.stderr}")
        sys.exit(1)
    
    print(result.stdout)
    return result.stdout

def main():
    """Función principal del script."""
    args = parse_args()
    
    # Crear la aplicación Flask con la configuración adecuada
    app = create_app(os.getenv('FLASK_ENV') or 'default')
    
    # Ejecutar el comando correspondiente
    with app.app_context():
        if args.command == 'init':
            run_flask_command('flask db init')
            print("Migraciones inicializadas correctamente.")
        
        elif args.command == 'migrate':
            run_flask_command(f'flask db migrate -m "{args.message}"')
            print(f"Migración generada con mensaje: {args.message}")
            print("Revisa el script generado antes de aplicarlo.")
        
        elif args.command == 'upgrade':
            run_flask_command(f'flask db upgrade {args.revision}')
            print(f"Base de datos actualizada a la revisión: {args.revision}")
        
        elif args.command == 'downgrade':
            run_flask_command(f'flask db downgrade {args.revision}')
            print(f"Base de datos revertida a la revisión: {args.revision}")
        
        elif args.command == 'history':
            run_flask_command('flask db history')
        
        elif args.command == 'current':
            run_flask_command('flask db current')
        
        else:
            print("Comando no reconocido. Usa --help para ver los comandos disponibles.")
            sys.exit(1)

if __name__ == '__main__':
    main() 