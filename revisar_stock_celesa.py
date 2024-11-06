import mysql.connector
import requests
import os
from datetime import datetime
import configparser

# Leer configuración desde config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Configuración de conexión a la base de datos
db_config = {
    'host': config['DATABASE']['HOST'],
    'user': config['DATABASE']['USER'],
    'password': config['DATABASE']['PASSWORD'],
    'database': config['DATABASE']['NAME'],
    'charset': 'utf8mb4'
}

# URL del archivo de datos
data_url = 'http://www.celesa.com/html/servicios_web/stock.php?fr_usuario=860720&fr_clave=Apricor20'
data_file_path = 'stockcelesa.csv'

def descargar_archivo():
    """Descarga el archivo de datos desde la URL especificada."""
    print("Descargando archivo de datos...")
    response = requests.get(data_url)
    with open(data_file_path, 'wb') as file:
        file.write(response.content)
    print("Archivo descargado exitosamente.")

def cargar_datos_archivo():
    """Carga los datos desde el archivo en un diccionario."""
    stock_data = {}
    with open(data_file_path, 'r') as file:
        for line in file:
            isbn, cnt = line.strip().split(';')
            stock_data[isbn] = int(cnt)
    return stock_data

def actualizar_stock():
    # Conectar a la base de datos
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Cargar los datos del archivo
    stock_data = cargar_datos_archivo()

    # Obtener todos los ISBN de la tabla celesa_stock
    cursor.execute("SELECT isbn, cnt FROM celesa_stock")
    db_data = {isbn: cnt for isbn, cnt in cursor.fetchall()}

    # Insertar o actualizar en celesa_stock y realizar verificaciones en celesa
    for isbn, cnt in stock_data.items():
        # Actualizar o insertar en celesa_stock
        if isbn in db_data:
            if db_data[isbn] != cnt:
                cursor.execute("UPDATE celesa_stock SET cnt = %s WHERE isbn = %s", (cnt, isbn))
                print(f"Actualizado en celesa_stock: {isbn} a cnt={cnt}")
        else:
            cursor.execute("INSERT INTO celesa_stock (isbn, cnt) VALUES (%s, %s)", (isbn, cnt))
            print(f"Insertado en celesa_stock: {isbn} con cnt={cnt}")

        # Verificar en la tabla celesa si existe el record_reference correspondiente
        cursor.execute("SELECT stock FROM celesa WHERE record_reference = %s", (isbn,))
        result = cursor.fetchone()

        if result is not None:  # Si el record_reference existe en celesa
            current_stock = result[0]

            if current_stock is None:
                # Si stock es NULL, actualizar con el valor del archivo y novedad a 'new'
                cursor.execute("UPDATE celesa SET stock = %s, novedad = 'new' WHERE record_reference = %s", (cnt, isbn))
                print(f"Actualizado en celesa: {isbn} con stock={cnt} y novedad='new' (stock era NULL)")
            elif current_stock != cnt:
                # Si stock tiene un valor diferente, actualizar con el nuevo valor y novedad a 'new'
                cursor.execute("UPDATE celesa SET stock = %s, novedad = 'new' WHERE record_reference = %s", (cnt, isbn))
                print(f"Actualizado en celesa: {isbn} con stock={cnt} y novedad='new' (stock cambiado)")
            else:
                print(f"Sin cambios para {isbn} en celesa (stock igual)")

    # Actualizar cnt a 0 en celesa_stock para ISBNs que no están en el archivo
    for isbn in db_data:
        if isbn not in stock_data:
            cursor.execute("UPDATE celesa_stock SET cnt = 0 WHERE isbn = %s", (isbn,))
            print(f"Actualizado en celesa_stock: {isbn} a cnt=0 (no encontrado en archivo)")

    # Guardar cambios en la base de datos
    conn.commit()
    cursor.close()
    conn.close()
    print("Actualización completada.")

def ejecutar_proceso():
    """Ejecuta el proceso completo de descarga, actualización y limpieza."""
    descargar_archivo()
    actualizar_stock()
    os.remove(data_file_path)  # Eliminar el archivo después del procesamiento
    print("Archivo de datos eliminado.")

if __name__ == '__main__':
    ejecutar_proceso()
