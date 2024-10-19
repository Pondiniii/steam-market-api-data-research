import requests
from secrets import webshare_proxy_api_key

def get_proxies():
    url = "https://proxy.webshare.io/api/proxy/list/"
    headers = {
        "Authorization": f"Token {webshare_proxy_api_key}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        proxy_data = response.json()
        proxies_list = []
        
        # Parsowanie odpowiedzi i przekształcanie do formatu SOCKS5
        for proxy in proxy_data['results']:
            proxy_format = {
                'socks5': f"socks5://{proxy['proxy_address']}:{proxy['ports']['socks5']}"
            }
            proxies_list.append(proxy_format)
        
        return proxies_list
    else:
        print(f"Błąd: {response.status_code}")
        return []

# Testowanie funkcji
proxies = get_proxies()
print(proxies)

