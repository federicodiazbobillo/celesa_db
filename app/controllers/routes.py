from flask import Blueprint, render_template, request
import mysql.connector
import configparser

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

@main.route('/', methods=['GET', 'POST'])
def buscar():
    data = None
    if request.method == 'POST':
        isbn = request.form.get('isbn')
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Ejecuta la consulta solo para el ISBN ingresado
        cursor.execute("SELECT * FROM celesa WHERE record_reference = %s", (isbn,))
        data = cursor.fetchall()
        
        cursor.close()
        conn.close()
    
    return render_template('index.html', data=data)
