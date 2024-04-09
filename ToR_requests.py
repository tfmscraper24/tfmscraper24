import requests
import stem.process
import time

def get_new_tor_ip():
    with stem.process.launch_tor_with_config(
        config={
            'SocksPort': '9100',
            'DataDirectory': '/tmp/tor',
            'ControlPort': '9151'
},
        init_msg_handler=print
) as controller:
        controller.authenticate()
        controller.signal(stem.signal.NEWNYM)
        return requests.get('https://httpbin.org/ip', proxies={'http': 'socks5://localhost:9100', 'https': 'socks5://localhost:9100'}).json()['origin']

def tor_requests(url, max_requests):
    print(f"Realizando peticiones a {url} con TOR")
    for i in range(max_requests):
        if i % 4 == 0:
            print(f"Cambiando IP - Petición {i}")
            ip = get_new_tor_ip()
            print(f"Nueva IP: {ip}")
        print(f"Peticion {i}: {requests.get(url, proxies={'http': 'socks5://localhost:9100', 'https': 'socks5://localhost:9100'}).json()['origin']}")
        time.sleep(2)

if __name__ == '__main__':
    url = 'https://httpbin.org/ip'
max_requests = 4
tor_requests(url, max_requests)
