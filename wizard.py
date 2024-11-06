import subprocess

def ejecutar_script(script_name):
    """Ejecuta un script de Python y espera a que termine."""
    print(f"\nEjecutando {script_name}...")
    result = subprocess.run(['python3', script_name])
    
    if result.returncode == 0:
        print(f"{script_name} ejecutado correctamente.\n")
    else:
        print(f"Error al ejecutar {script_name}.")
        exit(1)  # Detener el proceso si hay un error en cualquier script

# Ejecución secuencial de los scripts en el orden indicado
ejecutar_script('db_wizard.py')  # Requiere interacción del usuario
ejecutar_script('insert.py')
ejecutar_script('insert_celesa_descuentos.py')
ejecutar_script('revisar_stock_celesa.py')

print("Proceso de configuración completado.")

