import pandas as pd
import mysql.connector

# Configuración de conexión a la base de datos
db_config = {
    'host': 'localhost',
    'user': 'fede',
    'password': 'B9j3d18.01',
    'database': 'libreria',
    'charset': 'utf8mb4'
}

# Ruta al archivo Excel
excel_file_path = 'apricordescuentos.xlsx'

def insertar_datos():
    # Cargar datos desde el archivo Excel
    df = pd.read_excel(excel_file_path)

    # Conectar a la base de datos
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Consulta SQL para insertar datos en la tabla celesa_descuentos
    sql = """
    INSERT INTO celesa_descuentos (cliente, nombre_cliente, editorial, nombre_editorial, tipo, descripcion_tipo, dto)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    # Iterar sobre cada fila y ejecutar la inserción
    for _, row in df.iterrows():
        data = (
            str(row['Cliente']),
            str(row['Nombre Cliente']),
            str(row['Editorial']),
            str(row['Nombre Editorial']),
            int(row['Tipo']),
            str(row['Descripcion Tipo']),
            float(row['Dto'])
        )
        cursor.execute(sql, data)
    
    conn.commit()
    cursor.close()
    conn.close()

    print("Datos insertados exitosamente en la tabla celesa_descuentos.")

if __name__ == '__main__':
    insertar_datos()
