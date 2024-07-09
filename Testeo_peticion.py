import requests
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller

# URLs de los foros a verificar
urls = [
    'http://omegalock5zxwbhswbisc42o2q2i54vdulyvtqqbudqousisjgc7j7yd.onion/',
    'http://wn6vonooq6fggjdgyocp7bioykmfjket7sbp47cwhgubvowwd7ws5pyd.onion/ ',
    'http://bianlivemqbawcco4cx4a672k2fip3guyxudzurfqvdszafam3ofqgqd.onion/'
]

# Configuración de Tor
TOR_PROXY = 'socks5h://127.0.0.1:9050'
TOR_CONTROL_PORT = 9051
TOR_PASSWORD = 'your_password_here'  # Cambia esto por tu contraseña de control de Tor


def renew_tor_ip():
    """Renueva la IP de Tor."""
    with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
        controller.authenticate(password=TOR_PASSWORD)
        controller.signal(Signal.NEWNYM)


def get_tor_session():
    """Obtiene una sesión de requests configurada para usar Tor."""
    session = requests.Session()
    session.proxies = {
        'http': TOR_PROXY,
        'https': TOR_PROXY,
    }
    return session


def check_urls(urls):
    """Comprueba las URLs y devuelve su estado de conexión."""
    session = get_tor_session()
    status_results = {}

    for url in urls:
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                status_results[url] = 'Conexión exitosa'
            else:
                status_results[url] = f'Error: {response.status_code}'
        except requests.RequestException as e:
            status_results[url] = f'Error de conexión: {e}'

        # Renueva la IP de Tor después de cada petición para evitar bloqueos
        renew_tor_ip()

    return status_results


if __name__ == "__main__":
    results = check_urls(urls)
    for url, status in results.items():
        print(f'{url}: {status}')
