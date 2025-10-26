"""
Punto de entrada para ejecutar la aplicación Flask directamente.

Este script se invoca con `python -m backend` y es el responsable
de crear la instancia de la aplicación usando el patrón de fábrica
y de poner en marcha el servidor de desarrollo.
"""
from backend import create_app
import os

# 1. Crear la instancia de la aplicación llamando a la fábrica.
app = create_app()

# 2. Cuando este script es ejecutado, iniciar el servidor.
if __name__ == "__main__":
    # Obtener el puerto de la variable de entorno PORT, con 8080 como valor por defecto.
    # Esto es estándar para la mayoría de las plataformas de hosting.
    port = int(os.environ.get("PORT", 8080))
    
    # Iniciar el servidor de desarrollo de Flask.
    # host='0.0.0.0' es crucial para que el servidor sea visible
    # desde fuera del contenedor, permitiendo que el panel de vista previa se conecte.
    # debug=True activa el modo de depuración para obtener errores detallados.
    app.run(host='0.0.0.0', port=port, debug=True)
