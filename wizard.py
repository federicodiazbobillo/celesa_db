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
    result = subprocess.run(['venv/bin/python', '-m', 'pip', 'install', '--break-system-packages', '-r', 'requirements.txt'])
    
    if result.returncode == 0:
        print("Instalación de paquetes completada.\n")
    else:
        print("Error al instalar los paquetes.")
        exit(1)

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

# Crear entorno virtual, instalar requisitos y ejecutar scripts en secuencia
crear_entorno_virtual()
instalar_requerimientos()
ejecutar_script('db_wizard.py')  # Requiere interacción del usuario
ejecutar_script('insert.py')
ejecutar_script('insert_celesa_descuentos.py')
ejecutar_script('revisar_stock_celesa.py')

print("Proceso de configuración completado.")

# Iniciar la aplicación Flask al finalizar
iniciar_aplicacion_flask()

# Eliminar este script después de su ejecución
script_path = os.path.realpath(__file__)
try:
    os.remove(script_path)
    print(f"El script {script_path} ha sido eliminado.")
except Exception as e:
    print(f"No se pudo eliminar el script: {e}")
