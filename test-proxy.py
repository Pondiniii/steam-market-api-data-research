import requests
from proxy_tools import get_proxies

# Funkcja testująca proxy
def test_proxy(proxy):
    try:
        # Wykonaj żądanie do Steam Community z przekazanym proxy przez HTTPS
        response = requests.get(
            'https://steamcommunity.com/market/priceoverview/?appid=730&currency=3&market_hash_name=StatTrak%E2%84%A2%20M4A1-S%20|%20Hyper%20Beast%20(Minimal%20Wear)', 
            proxies=proxy, 
            timeout=10
        )
        if response.status_code == 200:
            print(f"Proxy {proxy} działa na HTTPS. Odpowiedź z Steam Community: OK")
            print(response.text[:500])  # Wyświetl tylko pierwsze 500 znaków odpowiedzi
        else:
            print(f"Proxy {proxy} nie działa na HTTPS. Kod odpowiedzi: {response.status_code}")
    except requests.exceptions.ProxyError as e:
        print(f"Proxy {proxy} nie działa. Błąd: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas połączenia: {e}")

# Pobierz proxy z API
proxies_list = get_proxies()

# Testuj każde proxy
for proxy in proxies_list:
    # Przekształcenie na format SOCKS5 z obsługą HTTPS
    proxy_socks5 = {
        'http': f"socks5://{proxy['proxy_address']}:{proxy['ports']['socks5']}",
        'https': f"socks5://{proxy['proxy_address']}:{proxy['ports']['socks5']}"
    }
    test_proxy(proxy_socks5)

