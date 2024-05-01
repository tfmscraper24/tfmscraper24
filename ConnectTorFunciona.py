import requests
import json
from bs4 import BeautifulSoup
import stem.process

def get_new_tor_ip():
    with stem.process.launch_tor_with_config(
        config={
            'SocksPort': '9100',
            'DataDirectory': '/tmp/tor',
            'ControlPort': '9151'
},
        init_msg_handler=lambda _: print("Tor init message: " + _)
    ) as controller:
        controller.authenticate()
        controller.signal(stem.signal.NEWNYM)
        return requests.get('https://breachforums.st/Forum-Sellers-Place?sortby=started&order=desc&datecut=9999&prefix=1', proxies={'http': 'socks5://localhost:9100', 'https': 'socks5://localhost:9100'}).json()['origin']

def scrape_forum(url, country, company_name):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    # Buscar y extraer datos relacionados con el país y la empresa
# Ajustar esta parte según la estructura HTML del foro real
# Por ejemplo, buscando en etiquetas específicas o atributos HTML
# country_data = soup.find_all(text=country)
# company_data = soup.find_all(text=company_name)
# Procesar los datos encontrados y crear una estructura de datos
# results = []
# for country_datum, company_datum in zip(country_data, company_data):
#     result = {
#         'country': country_datum.strip(),
#         'company_name': company_datum.strip()
#     }
#     results.append(result)
    return results

def tor_requests(url, country, company_name, max_requests):
    print(f"Realizando peticiones a {url} con TOR")
    for i in range(max_requests):
        ip = get_new_tor_ip()
        print(f"Petición {i}: IP {ip}")
        results = scrape_forum(url, country, company_name)
        with open(f'results_{i}.json', 'w', encoding='utf-8') as file:
        # Write results to JSON file
            json.dump(results, file, ensure_ascii=False, indent=4)