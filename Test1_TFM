import requests
from bs4 import BeautifulSoup
import json

def scrape_forum(url, country, company_name):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    # Buscar y extraer datos relacionados con el país y la empresa
country_data = soup.find_all(text=country)
    company_data = soup.find_all(text=company_name)

    # Procesar los datos encontrados y crear una estructura de datos
results = []
    for country_datum, company_datum in zip(country_data, company_data):
        result = {
            'country': country_datum.strip(),
            'company_name': company_datum.strip()
        }
        results.append(result)

    return results

if __name__ == '__main__':
    url = 'https://example-forum.com'
country = 'Spain'
company_name = 'Example Company'
results = scrape_forum(url, country, company_name)

    with open('results.json', 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)
        print("Results saved to results.json")
