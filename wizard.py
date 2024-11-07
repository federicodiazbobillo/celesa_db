import subprocess
import os

def crear_entorno_virtual():
    """Crea un entorno virtual si no existe."""
    if not os.path.exists('venv'):
        print("\nCreando entorno virtual...")
        subprocess.run(['python3', '-m', 'venv', 'venv'])
        print("Entorno virtual creado.\n")
    else:
        print("El entorno virtual ya existe.\n")

def instalar_requerimientos():
    """Instala los paquetes desde requirements.txt en el entorno virtual."""
    print("\nInstalando paquetes de requirements.txt en el entorno virtual...")
    result = subprocess.run(['venv/bin/pip', 'install', '-r', 'requirements.txt'])
    
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

# Crear entorno virtual, instalar requisitos y ejecutar scripts en secuencia
crear_entorno_virtual()
instalar_requerimientos()
ejecutar_script('db_wizard.py')  # Requiere interacción del usuario
ejecutar_script('insert.py')
ejecutar_script('insert_celesa_descuentos.py')
ejecutar_script('revisar_stock_celesa.py')

print("Proceso de configuración completado.")
