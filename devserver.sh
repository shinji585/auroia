#!/bin/bash

# Establecer variables de entorno para el desarrollo
export FLASK_ENV=development
export DEBUG=true # Para activar el modo debug en nuestro script

# Activar el entorno virtual
source .venv/bin/activate

# Ejecutar la aplicación usando el módulo del paquete
# El puerto es manejado por la variable de entorno PORT que Firebase Studio provee.
echo "Iniciando el servidor de Flask en modo de desarrollo..."
python -m backend
