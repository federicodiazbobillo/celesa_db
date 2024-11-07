import subprocess
import os
import socket
import shutil

def crear_entorno_virtual():
    """Elimina el entorno virtual si existe y luego lo crea."""
    if os.path.exists('venv'):
        print("\nEliminando el entorno virtual existente...")
        shutil.rmtree('venv')
        print("Entorno virtual eliminado.\n")

    print("Creando nuevo entorno virtual...")
    subprocess.run(['python3', '-m', 'venv', 'venv'])
    print("Entorno virtual creado.\n")

def instalar_requerimientos():
    """Instala los paquetes desde requirements.txt en el entorno virtual usando python -m pip."""
    print("\nInstalando paquetes de requirements.txt en el entorno virtual...")
    result = subprocess.run(['venv/bin/python', '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    if result.returncode == 0:
        print("Instalación de paquetes completada.\n")
    else:
        print("Error al instalar los paquetes.")
        exit(1)

def crear_estructura_proyecto():
    """Crea la estructura de carpetas y archivos para la aplicación Flask."""
    print("\nCreando estructura del proyecto...")

    # Carpetas principales
    os.makedirs('app/templates', exist_ok=True)
    os.makedirs('app/static', exist_ok=True)
    os.makedirs('app/models', exist_ok=True)
    os.makedirs('app/controllers', exist_ok=True)

    # Archivos base
    with open('app/__init__.py', 'w') as f:
        f.write("""
from flask import Flask
from .controllers.routes import main

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.register_blueprint(main)
    return app
""")

    with open('app/controllers/routes.py', 'w') as f:
        f.write("""
from flask import Blueprint, render_template
import mysql.connector
import configparser

# Lee la configuración de la base de datos
config = configparser.ConfigParser()
config.read('config.ini')
db_config = {
    'host': config['DATABASE']['HOST'],
    'user': config['DATABASE']['USER'],
    'password': config['DATABASE']['PASSWORD'],
    'database': config['DATABASE']['NAME']
}

main = Blueprint('main', __name__)

@main.route('/')
def index():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM celesa")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', data=data)
""")

    with open('app/templates/index.html', 'w') as f:
        f.write("""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Datos de Celesa</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
</head>
<body>
    <h1>Listado de Datos de Celesa</h1>
    <table border="1">
        <thead>
            <tr>
                {% for key in data[0].keys() %}
                    <th>{{ key }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in data %}
                <tr>
                    {% for value in row.values() %}
                        <td>{{ value }}</td>
                    {% endfor %}
                </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
""")

    with open('run.py', 'w') as f:
        f.write("""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
""")

    print("Estructura del proyecto creada.\n")

def ejecutar_script(script_name):
    """Ejecuta un script de Python en el entorno virtual y espera a que termine."""
    print(f"\nEjecutando {script_name}...")
    result = subprocess.run(['venv/bin/python', script_name])
    
    if result.returncode == 0:
        print(f"{script_name} ejecutado correctamente.\n")
    else:
        print(f"Error al ejecutar {script_name}.")
        exit(1)  # Detener el proceso si hay un error en cualquier script

def puerto_disponible(puerto):
    """Verifica si el puerto está disponible."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', puerto)) != 0

def iniciar_aplicacion_flask():
    """Solicita el puerto y arranca la aplicación Flask en el puerto especificado."""
    while True:
        try:
            puerto = int(input("Ingrese el puerto para iniciar la aplicación Flask (por defecto 5000): ") or 5000)
            if not puerto_disponible(puerto):
                print(f"El puerto {puerto} ya está en uso. Intente con otro.")
            else:
                break
        except ValueError:
            print("Por favor, ingrese un número válido de puerto.")

    print(f"Iniciando aplicación Flask en el puerto {puerto}...")
    subprocess.run(['venv/bin/python', 'run.py', '--host', '0.0.0.0', '--port', str(puerto)])

# Crear entorno virtual, instalar requisitos, crear estructura de Flask y ejecutar scripts en secuencia
crear_entorno_virtual()
instalar_requerimientos()
crear_estructura_proyecto()
ejecutar_script('db_wizard.py')  # Requiere interacción del usuario
ejecutar_script('insert.py')
ejecutar_script('insert_celesa_descuentos.py')
ejecutar_script('revisar_stock_celesa.py')

print("Proceso de configuración completado.")

# Iniciar la aplicación Flask al finalizar
iniciar_aplicacion_flask()
