import os
import pymysql
from dotenv import load_dotenv
from flask import Flask, render_template, request
from hashids import Hashids
from werkzeug.exceptions import InternalServerError

load_dotenv()

app = Flask(__name__, static_folder='static')
domain_url = os.getenv("DOMAIN_URL", "https://bolturl.site") 
hashids_salt = os.getenv("HASHIDS_SALT")
hashids = Hashids(salt=hashids_salt, min_length=4)  
connection = pymysql.connect(
        host=os.getenv("DATABASE_HOST"),
        user=os.getenv("DATABASE_USERNAME"),
        passwd=os.getenv("DATABASE_PASSWORD"),
        db=os.getenv("DATABASE"),
        ssl={"ssl_accept": "strict"}
    )

with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INT AUTO_INCREMENT PRIMARY KEY,
                original_url VARCHAR(255) NOT NULL,
                short_url VARCHAR(255) NOT NULL
            )
        """)
def is_valid(url):
    url = url.lower()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url
def proccess_input(original_url):
    with connection.cursor() as cursor:
        validated_url = is_valid(original_url)
        cursor.execute("INSERT INTO urls (original_url, short_url) VALUES (%s, %s)", (validated_url, ''))
        url_id = cursor.lastrowid
        url_code = hashids.encode(url_id)
        complete_url = f"{domain_url}/{url_code}"
        cursor.execute("UPDATE urls SET short_url = %s WHERE id = %s", (complete_url, url_id))
        return complete_url
    
@app.route('/')
def index():
    return render_template('index.html', bolted_url=None)
@app.route('/bolted', methods=['POST'])
def acortar():
    original_url = request.form['url']
    bolted_url = proccess_input(original_url)
    return render_template('index.html', bolted_url=bolted_url)

@app.route('/<url_code>')
def redirigir(url_code):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT original_url FROM urls WHERE short_url = %s", (f"{domain_url}/{url_code}",))
            result = cursor.fetchone()

            if result:
                original_url = result[0]
                return render_template('redirect.html', original_url=original_url)
            else:
                return "URL no encontrada"
    except InternalServerError:
        # Manejar la excepción aquí
        return "Error interno del servidor"
    
@app.route('/user_agreements')
def user_agreements():
    return render_template('user_agreements.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000)