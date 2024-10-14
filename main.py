import json
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
    # Connect to the database
    connection = psycopg2.connect(**db_secrets)
    
    # For development purposes, we're processing only the first page
    start = 0
    count = 100  # Maximum number of listings per request
    url = gen_market_link(start, count)
    
    # Implement rate limit for Steam (1 request per minute)
    steam_rate_limit()
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching data from {url}")
        return
    print(response)
    with open('response-rate-limit.json', 'w') as file:
        json.dump(response.json(), file, indent=4)
    print(response['total_count'])
    print(json.*
    # Parse the response
    listings = responce_parser(response)
    
    # Process each listing individually
    for listing in listings:
        listing_id = listing['listing_id']
        
        # Check if we should process this listing
        if not should_process_listing(listing_id, connection):
            print(f"Skipping listing {listing_id}, already processed.")
            continue
        
        # Insert the listing into the database if it doesn't exist
        insert_listing_into_db(listing, connection)
        
        # Fetch paint_seed for this listing
        paint_seed = fetch_paint_seed(listing['inspection_link'])
        print(f"Paint seed for listing {listing_id}: {paint_seed}")
        
        # Update the database with the fetched paint_seed
        cursor = connection.cursor()
        cursor.execute("UPDATE listings SET paint_seed = %s WHERE listing_id = %s", (paint_seed, listing_id))
        connection.commit()
        cursor.close()
        
        # Check criteria and send notification
        if paint_seed is not None and meets_criteria(paint_seed):
            message = f"Oferta {listing_id} spełnia kryteria z paint_seed {paint_seed}. {listing['inspection_link']} cena = {listing['price']}"
            print(message)
            send_telegram_message(message)
        
        # Wait to avoid exceeding the rate limit of the paint_seed API
        time.sleep(fetch_paint_seed_rate_limit())
    
    # Close the database connection
    connection.close()

# Implement rate limit for Steam
steam_last_request_time = 0
def steam_rate_limit():
    global steam_last_request_time
    current_time = time.time()
    elapsed_time = current_time - steam_last_request_time
    if elapsed_time < 60:
        sleep_time = 60 - elapsed_time
        print(f"Waiting {sleep_time:.2f} seconds before the next Steam API request.")
        time.sleep(sleep_time)
    steam_last_request_time = time.time()

# Implement rate limit for fetch_paint_seed
fetch_paint_seed_last_request_time = 0
def fetch_paint_seed_rate_limit():
    global fetch_paint_seed_last_request_time
    current_time = time.time()
    elapsed_time = current_time - fetch_paint_seed_last_request_time
    min_interval = 60 / 8  # 8 requests per minute
    if elapsed_time < min_interval:
        sleep_time = min_interval - elapsed_time
        print(f"Waiting {sleep_time:.2f} seconds before the next csinventory API request.")
        fetch_paint_seed_last_request_time = current_time + sleep_time
        return sleep_time
    else:
        fetch_paint_seed_last_request_time = current_time
        return 0

def fetch_paint_seed(inspection_link):
    # Fetch paint_seed from the API with rate limiting
    api_key = api_secrets['paint_seed_api_key']
    encoded_link = urllib.parse.quote(inspection_link, safe='')
    api_url = f"https://csinventoryapi.com/api/v1/inspect?api_key={api_key}&url={encoded_link}"
    
    print(f"Sending request to csinventory API: {api_url}")
    response = requests.get(api_url)
    
    if response.status_code != 200:
        print(f"Error fetching paint_seed for {inspection_link}")
        return None
    data = response.json()
    if 'iteminfo' in data and 'paintseed' in data['iteminfo']:
        return data['iteminfo']['paintseed']
    else:
        return None

def meets_criteria(paint_seed):
    numbers = [490, 148, 109, 116, 134, 158, 168, 225, 338, 354, 356, 365, 370, 386, 406, 426, 433, 441, 483, 537, 542, 592, 607, 611, 651, 668, 673, 696, 730, 743, 820, 846, 856, 857, 870, 876, 878, 882, 898, 900, 925, 942, 946, 951, 953, 970, 998]
    return paint_seed in numbers

# Implement the function to send a notification via Telegram
async def send_telegram_message_async(message):
    try:
        bot = Bot(token=bot_token)
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            disable_web_page_preview=False
        )
    except Exception as e:
        print(f"Error sending message: {e}")

def send_telegram_message(message):
    asyncio.run(send_telegram_message_async(message))

def should_process_listing(listing_id, connection):
    cursor = connection.cursor()
    query = "SELECT paint_seed FROM listings WHERE listing_id = %s"
    cursor.execute(query, (listing_id,))
    result = cursor.fetchone()
    cursor.close()
    if result is not None:
        paint_seed = result[0]
        if paint_seed is None:
            # Listing exists but paint_seed is NULL, need to process
            return True
        else:
            # Listing exists and paint_seed is not NULL, skip processing
            return False
    else:
        # Listing does not exist, need to process
        return True

if __name__ == "__main__":
    main()

