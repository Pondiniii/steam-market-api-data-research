import requests
import psycopg2
from secrets import db_secrets, api_secrets
from database import insert_listing_into_db
from request_tools import gen_market_link, responce_parser
import time
import urllib.parse

def main():
    # Połączenie z bazą danych
    connection = psycopg2.connect(**db_secrets)
    
    # Krok 1: Generowanie linku i pobranie total_count
    url = gen_market_link(0, 1)
    response = requests.get(url)
    response_json = response.json()
    total_count = response_json['total_count']
    print(f"Całkowita liczba ofert: {total_count}")
    
    # Obliczenie liczby stron
    count_per_request = 100  # Maksymalna liczba ofert na jedno zapytanie
    total_pages = (total_count + count_per_request - 1) // count_per_request
    print(f"Liczba stron do przetworzenia: {total_pages}")
    
    # Krok 2 i 3: Pobieranie danych i przechodzenie przez strony
    for page in range(total_pages):
        start = page * count_per_request
        count = min(count_per_request, total_count - start)
        url = gen_market_link(start, count)
        response = requests.get(url)
        
        # Miejsce na wykonanie IP change (niezaimplementowane)
        # Tutaj można dodać kod zmieniający IP
        
        if response.status_code != 200:
            print(f"Błąd pobierania danych z {url}")
            continue
        
        # Krok 3: Parsowanie odpowiedzi
        listings = responce_parser(response)
        
        # Krok 4: Zapisanie danych do bazy
        for listing in listings:
            insert_listing_into_db(listing, connection)
        
        # Odczekanie, aby uniknąć limitów zapytań
        time.sleep(1)
    
    # Krok 5: Pobranie ofert bez paint_seed
    cursor = connection.cursor()
    cursor.execute("SELECT listing_id, inspection_link FROM listings WHERE paint_seed IS NULL")
    listings_to_update = cursor.fetchall()
    cursor.close()
    
    # Krok 6: Wyłączenie IP change (niezaimplementowane)
    # Tutaj można wyłączyć zmianę IP
    
    # Krok 7: Aktualizacja paint_seed przez API
    for listing_id, inspection_link in listings_to_update:
        paint_seed = fetch_paint_seed(inspection_link)
        # Aktualizacja bazy danych
        cursor = connection.cursor()
        cursor.execute("UPDATE listings SET paint_seed = %s WHERE listing_id = %s", (paint_seed, listing_id))
        connection.commit()
        cursor.close()
        
        # Krok 8: Sprawdzenie kryteriów i wysłanie powiadomienia
        if paint_seed is not None and meets_criteria(paint_seed):
            # Placeholder dla powiadomienia przez Telegram
            print(f"Oferta {listing_id} spełnia kryteria z paint_seed {paint_seed}.")
    
    # Zamknięcie połączenia z bazą danych
    connection.close()

def fetch_paint_seed(inspection_link):
    # Implementacja zapytania do API paint_seed
    api_key = api_secrets['paint_seed_api_key']
    encoded_link = urllib.parse.quote(inspection_link)
    api_url = f"https://csinventoryapi.com/api/v1/inspect?api_key={api_key}&url={encoded_link}"
    response = requests.get(api_url)
    if response.status_code != 200:
        print(f"Błąd pobierania paint_seed dla {inspection_link}")
        return None
    data = response.json()
    if 'iteminfo' in data and 'paintseed' in data['iteminfo']:
        return data['iteminfo']['paintseed']
    else:
        return None

def meets_criteria(paint_seed):
    # Definiowanie kryteriów dla paint_seed
    target_paint_seed = 420  # Przykładowa wartość do sprawdzenia
    return paint_seed == target_paint_seed

if __name__ == "__main__":
    main()

