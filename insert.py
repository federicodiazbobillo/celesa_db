import mysql.connector
import xml.etree.ElementTree as ET
from tqdm import tqdm
import requests
import zipfile
import os

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

# Configuración de la base de datos
host = 'localhost'
db = 'libreria'
user = 'fede'
password = 'B9j3d18.01'

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

# Consulta SQL
sql = """
INSERT INTO celesa (record_reference, notification_type, product_id_type, id_value, 
                    product_composition, product_form, measure_type, measurement, measure_unit_code,
                    title_text, contributor_role, person_name_inverted, language_code, 
                    extent_value, imprint_name, publisher_name, publisher_id_type, publisher_id,
                    publishing_status, publishing_date, supplier_name, product_availability, 
                    price_amount)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    notification_type=VALUES(notification_type),
    product_id_type=VALUES(product_id_type),
    id_value=VALUES(id_value),
    product_composition=VALUES(product_composition),
    product_form=VALUES(product_form),
    measure_type=VALUES(measure_type),
    measurement=VALUES(measurement),
    measure_unit_code=VALUES(measure_unit_code),
    title_text=VALUES(title_text),
    contributor_role=VALUES(contributor_role),
    person_name_inverted=VALUES(person_name_inverted),
    language_code=VALUES(language_code),
    extent_value=VALUES(extent_value),
    imprint_name=VALUES(imprint_name),
    publisher_name=VALUES(publisher_name),
    publisher_id_type=VALUES(publisher_id_type),
    publisher_id=VALUES(publisher_id),
    publishing_status=VALUES(publishing_status),
    publishing_date=VALUES(publishing_date),
    supplier_name=VALUES(supplier_name),
    product_availability=VALUES(product_availability),
    price_amount=VALUES(price_amount)
"""

# Cargar el archivo XML extraído
batch_size = 1000  # Tamaño del lote
batch_data = []

namespace = {'ns': 'http://ns.editeur.org/onix/3.0/reference'}
valid_languages = {'por', 'fre', 'ger', 'eng', 'ita', 'spa'}

print("Iniciando la lectura del archivo XML...")

try:
    with tqdm(desc="Procesando productos", unit=" productos") as pbar:
        for event, elem in ET.iterparse(xml_filename, events=('end',)):
            if elem.tag == '{http://ns.editeur.org/onix/3.0/reference}Product':
                record_reference = elem.findtext('ns:RecordReference', namespaces=namespace)
                if not record_reference:
                    elem.clear()
                    pbar.update(1)
                    continue

                notification_type = elem.findtext('ns:NotificationType', namespaces=namespace)
                
                # Obtener identificador del producto
                product_identifier = elem.find('ns:ProductIdentifier', namespaces=namespace)
                product_id_type = product_identifier.findtext('ns:ProductIDType', namespaces=namespace) if product_identifier is not None else None
                id_value = product_identifier.findtext('ns:IDValue', namespaces=namespace) if product_identifier is not None else None

                # Detalles descriptivos
                descriptive_detail = elem.find('ns:DescriptiveDetail', namespaces=namespace)
                product_composition = descriptive_detail.findtext('ns:ProductComposition', namespaces=namespace) if descriptive_detail is not None else None
                product_form = descriptive_detail.findtext('ns:ProductForm', namespaces=namespace) if descriptive_detail is not None else None

                # Medidas
                measure = descriptive_detail.find('ns:Measure', namespaces=namespace) if descriptive_detail is not None else None
                measure_type = measure.findtext('ns:MeasureType', namespaces=namespace) if measure is not None else None
                measurement = measure.findtext('ns:Measurement', namespaces=namespace) if measure is not None else None
                measure_unit_code = measure.findtext('ns:MeasureUnitCode', namespaces=namespace) if measure is not None else None

                # Título y contribuyente
                title_detail = descriptive_detail.find('ns:TitleDetail', namespaces=namespace) if descriptive_detail is not None else None
                title_element = title_detail.find('ns:TitleElement', namespaces=namespace) if title_detail is not None else None
                title_text = title_element.findtext('ns:TitleText', namespaces=namespace) if title_element is not None else None

                contributor = descriptive_detail.find('ns:Contributor', namespaces=namespace) if descriptive_detail is not None else None
                contributor_role = contributor.findtext('ns:ContributorRole', namespaces=namespace) if contributor is not None else None
                person_name_inverted = contributor.findtext('ns:PersonNameInverted', namespaces=namespace) if contributor is not None else None

                # Idioma y extensión
                language = descriptive_detail.find('ns:Language', namespaces=namespace) if descriptive_detail is not None else None
                language_code = language.findtext('ns:LanguageCode', namespaces=namespace) if language is not None else None

                # Filtrar solo los idiomas válidos
                if language_code not in valid_languages:
                    elem.clear()
                    pbar.update(1)
                    continue

                extent = descriptive_detail.find('ns:Extent', namespaces=namespace) if descriptive_detail is not None else None
                extent_value = int(extent.findtext('ns:ExtentValue', namespaces=namespace)) if extent is not None and extent.findtext('ns:ExtentValue', namespaces=namespace) else None

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

                publishing_status = publishing_detail.findtext('ns:PublishingStatus', namespaces=namespace) if publishing_detail is not None else None
                publishing_date = publishing_detail.find('ns:PublishingDate').findtext('ns:Date', namespaces=namespace) if publishing_detail is not None and publishing_detail.find('ns:PublishingDate') is not None else None

                # Detalles de suministro y precio solo para EUR y PriceType 01
                price_amount = None
                for price in elem.findall('ns:ProductSupply/ns:SupplyDetail/ns:Price', namespaces=namespace):
                    currency_code = price.findtext('ns:CurrencyCode', namespaces=namespace)
                    price_type = price.findtext('ns:PriceType', namespaces=namespace)
                    if currency_code == 'EUR' and price_type == '01':
                        price_amount = price.findtext('ns:PriceAmount', namespaces=namespace)
                        break

                supplier_element = elem.find('ns:ProductSupply/ns:SupplyDetail/ns:Supplier', namespaces=namespace)
                supplier_name = supplier_element.findtext('ns:SupplierName', namespaces=namespace) if supplier_element is not None else None
                # Product availability
                product_availability = elem.findtext('ns:ProductSupply/ns:SupplyDetail/ns:ProductAvailability', namespaces=namespace)

                # Añadir datos al lote
                data = (
                    record_reference, notification_type, product_id_type, id_value,
                    product_composition, product_form, measure_type, measurement, measure_unit_code,
                    title_text, contributor_role, person_name_inverted, language_code,
                    extent_value, imprint_name, publisher_name, publisher_id_type, publisher_id,
                    publishing_status, publishing_date, supplier_name, product_availability, 
                    price_amount
                )
                batch_data.append(data)

                elem.clear()  # Limpiar el elemento para liberar memoria
                pbar.update(1)

                # Insertar cuando se alcanza el tamaño del lote
                if len(batch_data) >= batch_size:
                    cursor.executemany(sql, batch_data)
                    conn.commit()
                    batch_data = []  # Reiniciar el lote después de la inserción

        # Insertar los elementos restantes después de la iteración
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
