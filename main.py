import requests
import psycopg2
from secrets import db_secrets, api_secrets, bot_token, chat_id
from database import insert_listing_into_db
from request_tools import gen_market_link, responce_parser
import time
import urllib.parse
import asyncio
from telegram import Bot

def main():
    # Połączenie z bazą danych
    connection = psycopg2.connect(**db_secrets)
    
    # Dla celów deweloperskich, przetwarzamy tylko pierwszą stronę
    start = 0
    count = 100  # Maksymalna liczba ofert na jedno zapytanie
    url = gen_market_link(start, count)
    
    # Implementacja rate limit dla Steam (1 request na minutę)
    steam_rate_limit()
    
    response = requests.get(url)
    print(response.json())
    if response.status_code != 200:
        print(f"Błąd pobierania danych z {url}")
        return
    
    # Parsowanie odpowiedzi
    listings = responce_parser(response)
    
    # Przetwarzanie każdego wpisu indywidualnie
    for listing in listings:
        # Zapisanie danych do bazy
        insert_listing_into_db(listing, connection)
        
        # Pobranie paint_seed dla danego wpisu
        paint_seed = fetch_paint_seed(listing['inspection_link'])
        print(f"Paint seed dla listing {listing['listing_id']}: {paint_seed}")
        
        # Aktualizacja bazy danych
        cursor = connection.cursor()
        cursor.execute("UPDATE listings SET paint_seed = %s WHERE listing_id = %s", (paint_seed, listing['listing_id']))
        connection.commit()
        cursor.close()
        
        # Sprawdzenie kryteriów i wysłanie powiadomienia
        if paint_seed is not None and meets_criteria(paint_seed):
            message = f"Oferta {listing['listing_id']} spełnia kryteria z paint_seed {paint_seed}. {listing['inspection_link']}"
            print(message)
            send_telegram_message(message)
        
        # Oczekiwanie, aby uniknąć przekroczenia limitu zapytań do API paint_seed
        time.sleep(fetch_paint_seed_rate_limit())
    
    # Zamknięcie połączenia z bazą danych
    connection.close()

# Implementacja limitu szybkości dla Steam
steam_last_request_time = 0
def steam_rate_limit():
    global steam_last_request_time
    current_time = time.time()
    elapsed_time = current_time - steam_last_request_time
    if elapsed_time < 60:
        sleep_time = 60 - elapsed_time
        print(f"Oczekiwanie {sleep_time:.2f} sekund przed kolejnym zapytaniem do Steam API.")
        time.sleep(sleep_time)
    steam_last_request_time = time.time()

# Implementacja limitu szybkości dla fetch_paint_seed
fetch_paint_seed_last_request_time = 0
def fetch_paint_seed_rate_limit():
    global fetch_paint_seed_last_request_time
    current_time = time.time()
    elapsed_time = current_time - fetch_paint_seed_last_request_time
    min_interval = 60 / 8  # 8 zapytań na minutę
    if elapsed_time < min_interval:
        sleep_time = min_interval - elapsed_time
        print(f"Oczekiwanie {sleep_time:.2f} sekund przed kolejnym zapytaniem do csinventory API.")
        fetch_paint_seed_last_request_time = current_time + sleep_time
        return sleep_time
    else:
        fetch_paint_seed_last_request_time = current_time
        return 0

def fetch_paint_seed(inspection_link):
    # Implementacja zapytania do API paint_seed z rate limiting
    api_key = api_secrets['paint_seed_api_key']
    encoded_link = urllib.parse.quote(inspection_link, safe='')
    api_url = f"https://csinventoryapi.com/api/v1/inspect?api_key={api_key}&url={encoded_link}"
    
    print(f"Wysyłanie zapytania do csinventory API: {api_url}")
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
    #return paint_seed == target_paint_seed
    return paint_seed

# Implementacja funkcji wysyłania powiadomienia przez Telegram

async def send_telegram_message_async(message):
    try:
        bot = Bot(token=bot_token)
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            # Usuń lub zakomentuj parse_mode
            # parse_mode='Markdown',
            disable_web_page_preview=False
        )
    except Exception as e:
        print(f"Błąd podczas wysyłania wiadomości: {e}")


def send_telegram_message(message):
    asyncio.run(send_telegram_message_async(message))

if __name__ == "__main__":
    main()

