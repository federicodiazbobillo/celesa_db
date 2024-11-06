import mysql.connector
import xml.etree.ElementTree as ET
from tqdm import tqdm
import requests
import zipfile
import os
import configparser

# Leer configuración de la base de datos desde config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Obtener valores de configuración
try:
    host = config['DATABASE']['HOST']
    db = config['DATABASE']['NAME']
    user = config['DATABASE']['USER']
    password = config['DATABASE']['PASSWORD']
except KeyError as e:
    print(f"Error en la configuración: faltan datos de la base de datos en config.ini ({e})")
    exit(1)

# URLs de descarga
total_url = 'https://www.celesa.com/html/servicios_web/onix.php?user=860720&password=Apricor20'
partial_url = 'https://www.celesa.com/html/servicios_web/onix_parcial.php?user=860720&password=Apricor20'

# Preguntar al usuario si desea el archivo total o parcial
archivo_tipo = input("¿Desea procesar el archivo total o parcial? (total/parcial): ").strip().lower()
if archivo_tipo == 'total':
    download_url = total_url
    zip_filename = 'Azeta_Catalogo_ONIX.zip'
    xml_filename = 'Azeta_Catalogo_ONIX.xml'
elif archivo_tipo == 'parcial':
    download_url = partial_url
    zip_filename = 'Azeta_Catalogo_ONIX_parcial.zip'
    xml_filename = 'Azeta_Catalogo_ONIX_parcial.xml'
else:
    print("Tipo de archivo no válido. Debe ser 'total' o 'parcial'.")
    exit(1)

# Descargar el archivo zip
print("Descargando archivo...")
response = requests.get(download_url)
with open(zip_filename, 'wb') as f:
    f.write(response.content)

# Descomprimir el archivo zip
with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
    zip_ref.extractall()

# Conectar a la base de datos
try:
    conn = mysql.connector.connect(
        host=host,
        database=db,
        user=user,
        password=password,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
except mysql.connector.Error as err:
    print(f"Error de conexión: {err}")
    exit(1)

# Consulta SQL actualizada con solo los campos necesarios
sql = """
INSERT INTO celesa (record_reference, title_text, person_name_inverted, language_code,
                    imprint_name, publisher_name, publisher_id_type, publisher_id,
                    publishing_date, price_amount, currency_code)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    title_text=VALUES(title_text),
    person_name_inverted=VALUES(person_name_inverted),
    language_code=VALUES(language_code),
    imprint_name=VALUES(imprint_name),
    publisher_name=VALUES(publisher_name),
    publisher_id_type=VALUES(publisher_id_type),
    publisher_id=VALUES(publisher_id),
    publishing_date=VALUES(publishing_date),
    price_amount=VALUES(price_amount),
    currency_code=VALUES(currency_code)
"""

# Cargar el archivo XML extraído
batch_size = 1000
batch_data = []

namespace = {'ns': 'http://ns.editeur.org/onix/3.0/reference'}
valid_languages = {'por', 'fre', 'ger', 'eng', 'ita', 'spa'}

print("Iniciando la lectura del archivo XML...")

try:
    with tqdm(desc="Procesando productos", unit=" productos") as pbar:
        for event, elem in ET.iterparse(xml_filename, events=('end',)):
            if elem.tag == '{http://ns.editeur.org/onix/3.0/reference}Product':
                record_reference = elem.findtext('ns:RecordReference', namespaces=namespace)
                
                # Título y contribuyente
                descriptive_detail = elem.find('ns:DescriptiveDetail', namespaces=namespace)
                title_detail = descriptive_detail.find('ns:TitleDetail', namespaces=namespace) if descriptive_detail is not None else None
                title_element = title_detail.find('ns:TitleElement', namespaces=namespace) if title_detail is not None else None
                title_text = title_element.findtext('ns:TitleText', namespaces=namespace) if title_element is not None else None

                contributor = descriptive_detail.find('ns:Contributor', namespaces=namespace) if descriptive_detail is not None else None
                person_name_inverted = contributor.findtext('ns:PersonNameInverted', namespaces=namespace) if contributor is not None else None

                # Idioma
                language = descriptive_detail.find('ns:Language', namespaces=namespace) if descriptive_detail is not None else None
                language_code = language.findtext('ns:LanguageCode', namespaces=namespace) if language is not None else None

                # Detalles de publicación
                publishing_detail = elem.find('ns:PublishingDetail', namespaces=namespace)
                imprint = publishing_detail.find('ns:Imprint', namespaces=namespace) if publishing_detail is not None else None
                imprint_name = imprint.findtext('ns:ImprintName', namespaces=namespace) if imprint is not None else None

                publisher = publishing_detail.find('ns:Publisher', namespaces=namespace) if publishing_detail is not None else None
                publisher_name = publisher.findtext('ns:PublisherName', namespaces=namespace) if publisher is not None else None

                # Obtener el tipo y el ID del publisher
                publisher_identifier = publisher.find('ns:PublisherIdentifier', namespaces=namespace) if publisher is not None else None
                publisher_id_type = int(publisher_identifier.findtext('ns:PublisherIDType', namespaces=namespace)) if publisher_identifier is not None else None
                publisher_id = publisher_identifier.findtext('ns:IDValue', namespaces=namespace) if publisher_identifier is not None else None

                # Fecha de publicación
                publishing_date = publishing_detail.find('ns:PublishingDate').findtext('ns:Date', namespaces=namespace) if publishing_detail is not None and publishing_detail.find('ns:PublishingDate') is not None else None

                # Detalles de precio solo para EUR y PriceType 01
                price_amount = None
                currency_code = None
                for price in elem.findall('ns:ProductSupply/ns:SupplyDetail/ns:Price', namespaces=namespace):
                    currency_code = price.findtext('ns:CurrencyCode', namespaces=namespace)
                    price_type = price.findtext('ns:PriceType', namespaces=namespace)
                    if currency_code == 'EUR' and price_type == '01':
                        price_amount = price.findtext('ns:PriceAmount', namespaces=namespace)
                        break

                # Añadir datos al lote
                data = (
                    record_reference, title_text, person_name_inverted, language_code,
                    imprint_name, publisher_name, publisher_id_type, publisher_id,
                    publishing_date, price_amount, currency_code
                )
                batch_data.append(data)

                elem.clear()  # Limpiar el elemento para liberar memoria
                pbar.update(1)

                # Insertar el lote si se alcanza el tamaño máximo
                if len(batch_data) >= batch_size:
                    cursor.executemany(sql, batch_data)
                    conn.commit()
                    batch_data = []  # Reiniciar el lote

        # Insertar cualquier dato restante después de procesar el archivo
        if batch_data:
            cursor.executemany(sql, batch_data)
            conn.commit()

except Exception as e:
    print(f"Error durante el procesamiento: {e}")

finally:
    cursor.close()
    conn.close()

print("Datos guardados correctamente en la base de datos.")

# Eliminar los archivos descargados y extraídos
os.remove(zip_filename)
os.remove(xml_filename)
print("Archivos temporales eliminados.")
