import requests
from bs4 import BeautifulSoup

# URL del sitio web que vamos a scrapear
url = "https://breachforums.st/Forum-Sellers-Place?sortby=started&order=desc&datecut=9999&prefix=1"

# Realizamos una solicitud HTTP GET al sitio web
response = requests.get(url)

# Verificamos si la solicitud fue exitosa (código de estado 200)
if response.status_code == 200:
    # Creamos un objeto BeautifulSoup para analizar el contenido HTML de la página
    soup = BeautifulSoup(response.content, "html.parser")

    # Encontramos todos los elementos con la clase "subject_new", que contienen los títulos y enlaces
    subjects = soup.find_all("span", class_="subject_new")

    # Iteramos sobre los elementos encontrados
    for subject in subjects:
        # Obtenemos el enlace del post
        link = subject.find("a")['href']

        # Obtenemos el título del post
        title = subject.find("a").text

        # Imprimimos el título y el enlace
        print("Título:", title)
        print("Enlace:", link)
        print("-------------------------------------")

else:
    # Si la solicitud no fue exitosa, mostramos un mensaje de error
    print("Error al obtener la página:", response.status_code)
