from bs4 import BeautifulSoup
import requests
import json
import openai  # Asegúrate de tener instalada la biblioteca OpenAI: pip install openai
import sqlite3

# Configura la clave de la API de OpenAI
openai.api_key = 'tu_clave_de_api_de_openai'

# Lista de URLs .onion
onion_urls = [
    "http://breached26tezcofqla4adzyn22notfqwcac7gpbrleg4usehljwkgqd.onion",
    "http://breachedm6qqmtc2ksrdhhtdr6o4erzudgx4blvkcxhyeruudtibizqd.onion",
    "http://breachedhr2hxxranvbogkth63cpxwdcelsetui4uqavejvsqes4thid.onion",
    "http://breachedetbw6gnud64wvuld3xkyrrbz5eijhvjbbix72izpegjdvcyd.onion",
    "http://breached4lhlibrqmzj7h2n4unu7wdzkg7gczcggufbqufwmmdraiyqd.onion"
]

# Subforo
subforum_path = "Forum-Sellers-Place?sortby=started&order=desc&datecut=9999&prefix=1"

# Contador de llamadas a la API
api_call_count = 0
max_api_calls = 10  # Establece un límite según tus necesidades

# Función para obtener una sesión de requests con soporte para proxies SOCKS para Tor
def get_tor_session():
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://localhost:9050',
        'https': 'socks5h://localhost:9050'
    }
    return session

# Función para construir la URL dinámica y raspar el foro
def build_dynamic_url():
    session = get_tor_session()

    for onion_url in onion_urls:
        full_url = f"{onion_url}/{subforum_path}"
        try:
            response = session.get(full_url)
            if response.status_code == 200:
                return full_url
            elif response.status_code == 403:
                print(f"Error de autorización al acceder a {full_url}. Cambiando IP y reintentando.")
                # Aquí podrías manejar la lógica de cambiar la IP de Tor si lo deseas.
            elif response.status_code == 500:
                print(f"Error del servidor (500) al acceder a {full_url}. Saliendo.")
                exit()
            else:
                print(f"Fallo al acceder a {full_url}: Código de estado {response.status_code}")
        except requests.RequestException as e:
            print(f"Error al acceder a {full_url}: {e}")
    return None

# Función para analizar un post utilizando OpenAI
def analyze_post(title, company, country):
    if not country:
        country = "País no localizado"
    if not company:
        company = "Empresa no localizada"

    prompt = f"Un usuario publicó un mensaje en BreachForum titulado: '{title}'. El post menciona una empresa '{company}' ubicada en '{country}'. Analiza el post y proporciona información."
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Función para raspar el foro y almacenar resultados en la base de datos
def scrape_forum_and_store(url, country, company_name, conn):
    session = get_tor_session()

    try:
        response = session.get(url)
        soup = BeautifulSoup(response.content, 'lxml')

        # Lista para almacenar los resultados del análisis
        results = []

        # Buscar todos los elementos con la clase "subject_new"
        subjects = soup.find_all("span", class_="subject_new")
        for subject in subjects:
            link = subject.find("a")['href']
            title = subject.find("a").text
            # Analizar el post utilizando OpenAI
            analysis_result = analyze_post(title, company_name, country)
            # Almacenar el resultado en la base de datos
            store_result_in_db(title, link, analysis_result, conn)

    except requests.RequestException as e:
        print(f"Error al acceder a {url}: {e}")

# Función para crear o conectar a la base de datos SQLite
def create_or_connect_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # Crear tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forum_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT,
            analysis_result TEXT
        )
    ''')
    conn.commit()
    return conn

# Función para almacenar resultados en la base de datos
def store_result_in_db(title, link, analysis_result, conn):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO forum_posts (title, link, analysis_result)
        VALUES (?, ?, ?)
    ''', (title, link, analysis_result))
    conn.commit()

# Código principal para ejecutar el scraping y almacenamiento
def main():
    db_name = 'forum_posts.db'
    conn = create_or_connect_db(db_name)
    print("Realizando peticiones con TOR")
    for i in range(10):  # Ajustar el rango según sea necesario
        url = build_dynamic_url()
        if url:
            scrape_forum_and_store(url, "EjemploPaís", "EjemploEmpresa", conn)
        else:
            print("Todas las URL .onion fallaron.")
    conn.close()

if __name__ == "__main__":
    main()
