from flask import Blueprint, render_template, request, g
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

# Definición del blueprint principal
main = Blueprint('main', __name__)
# Blueprint para Mercado Libre
mercado_libre_bp = Blueprint('mercado_libre', __name__, url_prefix='/mercado-libre')

# Blueprint para Celesa
celesa_bp = Blueprint('celesa', __name__, url_prefix='/celesa')

# Blueprint para Configuración
configuracion_bp = Blueprint('configuracion', __name__, url_prefix='/configuracion')

def verificar_meli():
    """Verifica la conexión a Mercado Libre y renueva el token si ha expirado."""
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT app_id, secret_key, access_token, refresh_token FROM meli_access LIMIT 1")
    meli_access = cursor.fetchone()

    if not meli_access or not meli_access['access_token']:
        cursor.close()
        conn.close()
        return False, None, None, None, None

    headers = {'Authorization': f"Bearer {meli_access['access_token']}"}
    response = requests.get("https://api.mercadolibre.com/users/me", headers=headers)

    # Si el token es válido, extraer los datos del usuario
    if response.status_code == 200:
        user_data = response.json()
        cursor.close()
        conn.close()
        return True, meli_access['access_token'], user_data.get('first_name'), user_data.get('last_name'), user_data.get('nickname')

    # Si el token ha expirado y hay un refresh_token, intenta renovarlo
    elif response.status_code == 401 and meli_access['refresh_token']:
        data = {
            'grant_type': 'refresh_token',
            'client_id': meli_access['app_id'],
            'client_secret': meli_access['secret_key'],
            'refresh_token': meli_access['refresh_token']
        }
        token_response = requests.post("https://api.mercadolibre.com/oauth/token", data=data)

        # Si la renovación es exitosa, actualiza el access_token y refresh_token en la base de datos
        if token_response.status_code == 200:
            new_tokens = token_response.json()
            new_access_token = new_tokens['access_token']
            new_refresh_token = new_tokens.get('refresh_token', meli_access['refresh_token'])
            
            # Actualiza los tokens en la base de datos
            update_query = """
            UPDATE meli_access 
            SET access_token = %s, refresh_token = %s 
            WHERE app_id = %s
            """
            cursor.execute(update_query, (new_access_token, new_refresh_token, meli_access['app_id']))
            conn.commit()

            # Intenta nuevamente obtener los datos del usuario con el nuevo token
            headers = {'Authorization': f"Bearer {new_access_token}"}
            response = requests.get("https://api.mercadolibre.com/users/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                cursor.close()
                conn.close()
                return True, new_access_token, user_data.get('first_name'), user_data.get('last_name'), user_data.get('nickname')
        else:
            print("Error al renovar el token:", token_response.json())

    cursor.close()
    conn.close()
    return False, None, None, None, None


# Context processor para hacer los datos de Mercado Libre disponibles en todas las plantillas
@main.app_context_processor
def inject_meli_status():
    """Inyecta el estado de conexión de Mercado Libre en el contexto de todas las plantillas."""
    conectado, access_token, first_name, last_name, nickname = verificar_meli()
    return {
        'conectado_a_meli': conectado,
        'access_token': access_token,
        'first_name': first_name,
        'last_name': last_name,
        'nickname': nickname
    }

# Página de inicio
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/inicio')
def inicio():
    return render_template('index.html')

# Función para buscar datos de Celesa
@main.route('/buscar-celesa', methods=['GET', 'POST'])
def buscar_celesa():
    data = None
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
    
    return render_template('buscar_celesa.html', data=data)

# Blueprint para Mercado Libre
mercado_libre_bp = Blueprint('mercado_libre', __name__, url_prefix='/mercado-libre')

@mercado_libre_bp.route('/publicaciones')
def publicaciones():
    return render_template('blank_page.html')

@mercado_libre_bp.route('/ventas')
def ventas():
    return render_template('blank_page.html')

# Blueprint para Celesa
celesa_bp = Blueprint('celesa', __name__, url_prefix='/celesa')

@celesa_bp.route('/buscar')
def buscar():
    return render_template('blank_page.html')

@celesa_bp.route('/publicar')
def publicar():
    return render_template('blank_page.html')

# Blueprint para Configuración
configuracion_bp = Blueprint('configuracion', __name__)

@configuracion_bp.route('/configuracion')
def configuracion():
    return render_template('blank_page.html')
