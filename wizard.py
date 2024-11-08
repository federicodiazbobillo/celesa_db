import configparser
import getpass
import mysql.connector
import os
import subprocess
import socket
import shutil
from mysql.connector import Error

# Variable global para controlar si se deben ejecutar scripts adicionales
omit_scripts = False

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
        exit(1)

def puerto_disponible(puerto):
    """Verifica si el puerto está disponible."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', puerto)) != 0

def crear_run_script(puerto):
    """Crea el archivo run.py con el puerto especificado por el usuario y acceso remoto activado."""
    run_content = f"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port={puerto}, debug=True)
"""
    with open('run.py', 'w') as run_file:
        run_file.write(run_content)
    print(f"Archivo run.py creado con el puerto {puerto}.\n")

def iniciar_aplicacion_flask():
    """Solicita el puerto, crea run.py, y arranca la aplicación Flask en el puerto especificado."""
    while True:
        try:
            puerto = int(input("Ingrese el puerto para iniciar la aplicación Flask (por defecto 5000): ") or 5000)
            if not puerto_disponible(puerto):
                print(f"El puerto {puerto} ya está en uso. Intente con otro.")
            else:
                break
        except ValueError:
            print("Por favor, ingrese un número válido de puerto.")

    crear_run_script(puerto)
    print(f"Iniciando aplicación Flask en el puerto {puerto}...")
    subprocess.run(['venv/bin/python', 'run.py'])

def setup_database_config():
    """Configura la base de datos y guarda las credenciales en config.ini."""
    global omit_scripts
    if os.path.exists('config.ini'):
        overwrite = input("El archivo config.ini ya existe. ¿Desea eliminarlo y continuar? (s/n): ").strip().lower()
        if overwrite == 's':
            os.remove('config.ini')
            print("Archivo config.ini eliminado. Continuando con la configuración...")
        else:
            print("Operación cancelada.")
            return

    config = configparser.ConfigParser()

    print("Configuración de la base de datos:")
    db_user = input("Usuario de la base de datos: ")
    db_password = getpass.getpass("Contraseña de la base de datos: ")
    db_host = input("Host de la base de datos (por defecto 'localhost'): ") or "localhost"

    try:
        print("\nVerificando la conexión al servidor de base de datos...")

        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password
        )
        cursor = connection.cursor()

        cursor.execute("SHOW DATABASES")
        bases_disponibles = [db[0] for db in cursor if db[0] not in ('information_schema', 'mysql', 'performance_schema', 'sys')]

        print("\nBases de datos disponibles:")
        for i, db_name in enumerate(bases_disponibles):
            print(f"{i + 1} - {db_name}")
        print("0 - Crear una nueva base de datos")

        opcion = int(input("\nSeleccione una base de datos (ingrese el número): "))
        if opcion == 0:
            db_name = input("Ingrese el nombre de la nueva base de datos: ")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"Base de datos '{db_name}' creada exitosamente.")
        else:
            db_name = bases_disponibles[opcion - 1]
            print(f"Usando la base de datos existente: {db_name}")

        connection.database = db_name

        # Guardar configuración
        config['DATABASE'] = {
            'HOST': db_host,
            'USER': db_user,
            'PASSWORD': db_password,
            'NAME': db_name
        }
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        print("\nConfiguración guardada exitosamente en config.ini")

        # Verificar si las tablas ya existen en la base seleccionada
        if tablas_existentes(connection):
            reemplazar = input("Las tablas ya existen. ¿Desea reemplazarlas? (s/n): ").strip().lower()
            if reemplazar == 's':
                eliminar_tablas(connection)
                execute_schema_sql(connection)
            else:
                omit_scripts = True
                os.environ['OMIT_SCRIPTS'] = 'true'
                print("Continuando sin crear tablas ni ejecutar archivos de carga de datos.")
        else:
            execute_schema_sql(connection)

    except Error as e:
        print(f"Error de conexión: {e}")
        print("No se pudo conectar al servidor de base de datos. Por favor, verifica el usuario y la contraseña.")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def tablas_existentes(connection):
    """Verifica si las tablas requeridas ya existen en la base de datos."""
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tablas = {table[0] for table in cursor.fetchall()}
        tablas_requeridas = {"celesa", "celesa_descuentos"}  # Especifica las tablas necesarias
        return tablas_requeridas.issubset(tablas)
    except Error as e:
        print(f"Error al verificar tablas existentes: {e}")
        return False

def eliminar_tablas(connection):
    """Elimina todas las tablas de la base de datos para permitir una creación limpia."""
    try:
        cursor = connection.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()
        for (tabla,) in tablas:
            cursor.execute(f"DROP TABLE {tabla}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        connection.commit()
        print("Todas las tablas existentes han sido eliminadas.")
    except Error as e:
        print(f"Error al eliminar tablas: {e}")

def execute_schema_sql(connection):
    """Ejecuta el script SQL de schema.sql para crear las tablas."""
    try:
        cursor = connection.cursor()

        # Leer el archivo schema.sql
        with open('schema.sql', 'r') as file:
            schema_sql = file.read()

        # Ejecutar el script SQL
        for statement in schema_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)

        connection.commit()
        print("Tablas creadas exitosamente usando schema.sql")

    except FileNotFoundError:
        print("Error: No se encontró el archivo schema.sql.")
    except Error as e:
        print(f"Error al ejecutar schema.sql: {e}")
    finally:
        cursor.close()

# Secuencia principal de configuración
crear_entorno_virtual()
instalar_requerimientos()
setup_database_config()

# Solo ejecuta scripts adicionales si OMIT_SCRIPTS no está configurado en True
if os.getenv('OMIT_SCRIPTS') != 'true':
    ejecutar_script('insert.py')
    ejecutar_script('insert_celesa_descuentos.py')
    ejecutar_script('revisar_stock_celesa.py')

print("Proceso de configuración completado.")
iniciar_aplicacion_flask()

# Eliminar este script después de su ejecución
script_path = os.path.realpath(__file__)
try:
    os.remove(script_path)
    print(f"El script {script_path} ha sido eliminado.")
except Exception as e:
    print(f"No se pudo eliminar el script: {e}")
