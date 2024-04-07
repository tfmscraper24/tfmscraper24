import requests
import json

# Parámetros de configuración
api_url = 'https://api.forum.com/search'
params = {
    'country': 'España',
    'company_name': 'Empresa Ejemplo'
}

# Realizar la solicitud HTTP y obtener la respuesta
response = requests.get(api_url, params=params)
if response.status_code != 200:
    print(f"Error: {response.status_code}, {response.reason}")
    exit()

# Procesar la respuesta JSON y guardarla en un archivo
response_data = response.json()
with open('results.json', 'w', encoding='utf-8') as file:
    json.dump(response_data, file, ensure_ascii=False, indent=4)

print("Resultados guardados en results.json")
