import configparser
import getpass
import mysql.connector
import os
from mysql.connector import Error

def setup_database_config():
    # Verificar si config.ini ya existe
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
    db_name = input("Nombre de la base de datos: ")
    db_host = input("Host de la base de datos (por defecto 'localhost'): ") or "localhost"

    # Probar la conexión antes de guardar la configuración
    try:
        print("\nVerificando la conexión al servidor de base de datos...")

        # Intentar conectar al servidor MySQL sin especificar la base de datos
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password
        )
        cursor = connection.cursor()
        
        # Intentar seleccionar la base de datos
        try:
            connection.database = db_name
            print("Conexión exitosa. La base de datos existe y las credenciales son correctas.")
        
        except mysql.connector.Error as err:
            # Si la base de datos no existe (error 1049), intentar crearla
            if err.errno == 1049:  # Error 1049: Unknown database
                print(f"La base de datos '{db_name}' no existe. Intentando crearla...")

                try:
                    cursor.execute(f"CREATE DATABASE {db_name}")
                    connection.database = db_name
                    print(f"Base de datos '{db_name}' creada exitosamente.")
                
                except mysql.connector.Error as err:
                    if err.errno == 1044:  # Error 1044: Access denied for user
                        print("Error: El usuario no tiene permisos para crear la base de datos.")
                        return
                    else:
                        print(f"Error al intentar crear la base de datos: {err}")
                        return

        # Guardar la configuración si la conexión y verificación fueron exitosas
        config['DATABASE'] = {
            'HOST': db_host,
            'USER': db_user,
            'PASSWORD': db_password,
            'NAME': db_name
        }

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        print("\nConfiguración guardada exitosamente en config.ini")

        # Ejecutar el archivo schema.sql para crear las tablas
        execute_schema_sql(connection)

    except Error as e:
        print(f"Error de conexión: {e}")
        print("No se pudo conectar al servidor de base de datos. Por favor, verifica el usuario y la contraseña.")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

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

if __name__ == "__main__":
    setup_database_config()
