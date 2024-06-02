import requests
import json
from bs4 import BeautifulSoup
import stem.control
import stem.signal
import openai  # Instala con: pip install openai

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


def get_new_tor_ip():
    """
    Obtiene una nueva dirección IP a través de Tor.

    Returns:
        str: La nueva dirección IP obtenida de Tor.
    """
    with stem.control.Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(stem.signal.NEWNYM)
        controller.close()

    return requests.get('https://api.ipify.org',
                        proxies={'http': 'socks5://localhost:9050', 'https': 'socks5://localhost:9050'}).text


def build_dynamic_url():
    """
    Intenta acceder a cada URL .onion con la ruta del subforo hasta que se reciba una respuesta exitosa.

    Returns:
        str: La URL exitosa o None si todas las URL fallan.
    """
    for onion_url in onion_urls:
        full_url = f"{onion_url}/{subforum_path}"
        try:
            response = requests.get(full_url,
                                    proxies={'http': 'socks5://localhost:9050', 'https': 'socks5://localhost:9050'})
            if response.status_code == 200:
                return full_url
            elif response.status_code == 403:
                print(f"Error de autorización al acceder a {full_url}. Cambiando IP y reintentando.")
                get_new_tor_ip()
            elif response.status_code == 500:
                print(f"Error del servidor (500) al acceder a {full_url}. Saliendo.")
                exit()
            else:
                print(f"Fallo al acceder a {full_url}: Código de estado {response.status_code}")
        except requests.RequestException as e:
            print(f"Error al acceder a {full_url}: {e}")
    return None


def analyze_post(title, company, country):
    """
    Analiza un post del foro utilizando ChatGPT y devuelve el resultado en formato JSON.

    Args:
        title (str): El título del post del foro.
        company (str): La empresa mencionada en el post.
        country (str): El país mencionado en el post.

    Returns:
        dict: Un objeto JSON que contiene los resultados del análisis.
    """
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


def scrape_forum(url, country, company_name):
    """
    Raspa el foro en busca de datos relacionados con el país y el nombre de la empresa dados.

    Args:
        url (str): La URL del foro a raspar.
        country (str): El país a buscar.
        company_name (str): El nombre de la empresa a buscar.
    """
    response = requests.get(url, proxies={'http': 'socks5://localhost:9050', 'https': 'socks5://localhost:9050'})
    soup = BeautifulSoup(response.content, 'lxml')

    # Lista para almacenar los resultados del análisis
    results = []

    # Buscar todos los elementos con la clase "subject_new"
    subjects = soup.find_all("span", class_="subject_new")
    for subject in subjects:
        link = subject.find("a")['href']
        title = subject.find("a").text
        # Analizar el post utilizando ChatGPT
        analysis_result = analyze_post(title, company_name, country)
        # Almacenar el resultado en un diccionario
        result = {
            "Título": title,
            "Enlace": link,
            "Resultado del Análisis": analysis_result
        }
        results.append(result)

    # Imprimir resultados en formato JSON con separadores
    for res in results:
        print(json.dumps(res, indent=4))
        print("-------------------------------------")


print("Realizando peticiones con TOR")
for i in range(10):  # Ajustar el rango según sea necesario
    if i % 4 == 0:
        print(f"Cambiando IP - Petición {i}")
        ip = get_new_tor_ip()
        print(f"Petición {i}: IP {ip}")

    # Construir y raspar la URL dinámica
    url = build_dynamic_url()
    if url:
        scrape_forum(url, "EjemploPaís", "EjemploEmpresa")
    else:
        print("Todas las URL .onion fallaron.")
