import requests
import time

# Lista proxy do testowania
proxies_list = [
    {"http": "45.140.211.104:50100", "https": "45.140.211.104:50100"},
    # Dodaj więcej proxy, jeśli chcesz testować więcej
]

# Funkcja rotacji proxy
def get_next_proxy(index):
    return proxies_list[index % len(proxies_list)]

# Funkcja do wysyłania zapytania do rapidmaker.pl z użyciem proxy
def check_rapidmaker(proxy_index):
    url = 'https://httpbin.org/ip'
    proxies = get_next_proxy(proxy_index)
    
    try:
        # Wysyłanie zapytania przez proxy
        response = requests.get(url, proxies=proxies, timeout=10)
        if response.status_code == 200:
            print(f"Proxy {proxy_index}: Odpowiedź poprawna")
            print(response.text)  # Wyświetlanie zawartości strony
        else:
            print(f"Proxy {proxy_index}: Błąd {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Proxy {proxy_index}: Nie udało się połączyć - {e}")

# Testowanie wszystkich proxy z zapytaniem do rapidmaker.pl
def main():
    proxy_index = 0
    while proxy_index < len(proxies_list):
        check_rapidmaker(proxy_index)
        proxy_index += 1
        time.sleep(2)  # Czas oczekiwania między zapytaniami, aby nie przeciążać serwera

if __name__ == "__main__":
    main()

