from flask import Blueprint, render_template, request
import mysql.connector
import configparser
import requests

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

def verificaMeli():
    """Verifica si está conectado a Mercado Libre mediante los campos app_id, secret_key y access_token."""
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    # Consulta para obtener app_id, secret_key, access_token y refresh_token
    cursor.execute("SELECT app_id, secret_key, access_token, refresh_token FROM meli_access LIMIT 1")
    meli_access = cursor.fetchone()
    
    # Verificar si app_id y secret_key están presentes
    if not meli_access or not meli_access['app_id'] or not meli_access['secret_key']:
        cursor.close()
        conn.close()
        return False, None, None, None, None
    
    # Verificar el access_token llamando a la API de Mercado Libre
    headers = {'Authorization': f"Bearer {meli_access['access_token']}"}
    response = requests.get("https://api.mercadolibre.com/users/me", headers=headers)
    
    # Si el token es válido, extraer nickname, first_name y last_name
    if response.status_code == 200:
        user_data = response.json()
        nickname = user_data.get("nickname")
        first_name = user_data.get("first_name")
        last_name = user_data.get("last_name")
        cursor.close()
        conn.close()
        return True, meli_access['access_token'], nickname, first_name, last_name

    # Si el token ha expirado, usar el refresh_token para renovarlo
    elif response.status_code == 401 and meli_access['refresh_token']:
        data = {
            'grant_type': 'refresh_token',
            'client_id': meli_access['app_id'],
            'client_secret': meli_access['secret_key'],
            'refresh_token': meli_access['refresh_token']
        }
        token_response = requests.post("https://api.mercadolibre.com/oauth/token", data=data)

        # Si la renovación es exitosa, actualizar el access_token y refresh_token en la base de datos
        if token_response.status_code == 200:
            new_tokens = token_response.json()
            new_access_token = new_tokens['access_token']
            new_refresh_token = new_tokens.get('refresh_token', meli_access['refresh_token'])
            
            # Actualizar los tokens en la base de datos
            update_query = """
            UPDATE meli_access 
            SET access_token = %s, refresh_token = %s 
            WHERE app_id = %s
            """
            cursor.execute(update_query, (new_access_token, new_refresh_token, meli_access['app_id']))
            conn.commit()

            # Intentar nuevamente obtener nickname, first_name y last_name
            headers = {'Authorization': f"Bearer {new_access_token}"}
            response = requests.get("https://api.mercadolibre.com/users/me", headers=headers)
            user_data = response.json() if response.status_code == 200 else {}
            nickname = user_data.get("nickname")
            first_name = user_data.get("first_name")
            last_name = user_data.get("last_name")
            
            cursor.close()
            conn.close()
            return True, new_access_token, nickname, first_name, last_name
        else:
            print("Error al renovar el token:", token_response.json())
    
    cursor.close()
    conn.close()
    return False, None, None, None, None

@main.route('/', methods=['GET', 'POST'])
def buscar():
    data = None
    conectado_a_meli, access_token, nickname, first_name, last_name = verificaMeli()  # Verifica la conexión a Mercado Libre
    
    if request.method == 'POST':
        isbn = request.form.get('isbn')
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT record_reference, title_text, price_amount, currency_code, stock, dto 
            FROM celesa, celesa_descuentos 
            WHERE celesa.publisher_id = celesa_descuentos.editorial 
              AND celesa.record_reference = %s 
            ORDER BY dto ASC 
            LIMIT 1
        """       
        # Ejecuta la consulta solo para el ISBN ingresado
        cursor.execute(query, (isbn,))
        data = cursor.fetchall()
        
        cursor.close()
        conn.close()
    
    return render_template('index.html', data=data, conectado_a_meli=conectado_a_meli, access_token=access_token, nickname=nickname, first_name=first_name, last_name=last_name)
