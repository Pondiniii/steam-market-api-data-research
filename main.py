import requests
import psycopg2
import logging
from secrets import db_secrets, bot_token, chat_id, webshare_proxy_api_key
from database import insert_listing_into_db
from request_tools import gen_market_link, response_parser
import time
import urllib.parse
import asyncio
from telegram import Bot
import traceback
import threading


def main():
    # Error timer starts with 30 min jail time
    error_backoff = 30 * 60
    paint_seed = None
    response = None

    while True:
        try:
            connection = psycopg2.connect(**db_secrets)
            for quality in ['Factory New', 'Minimal Wear', 'Field-Tested', 'Well-Worn', 'Battle-Scarred']:
                start = 0
                count = 100
                url = gen_market_link(start, count, quality)

                sleep_time = 5
                for _ in range(10):
                    proxy = get_next_proxy()
                    try:
                        response = requests.get(url, proxies=proxy, timeout=10)
                        if response.status_code == 200:
                            logging.info("Successfully fetched data.")
                            break
                    except requests.exceptions.ProxyError:
                        logging.warning(f"Proxy error with {proxy}, trying next proxy.")
                    except requests.exceptions.ConnectTimeout:
                        logging.warning(f"Timeout with proxy {proxy}, trying next proxy.")
                    except Exception as e:
                        logging.error(f"Other error: {e}")
                    time.sleep(sleep_time)
                    sleep_time += 5

                if response.status_code != 200:
                    raise ValueError(f"Failed to fetch data from {url} after 5 retries")

                total_count = response.json().get('total_count', 0)
                if total_count == 0:
                    raise ValueError(f"No listings found for quality '{quality}'.")

                max_pages = (total_count + count - 1) // count
                logging.info(f"Quality: {quality}. Total listings: {total_count}. Total pages to process: {max_pages}")

                for page in range(max_pages):
                    url = gen_market_link(start, count, quality)
                    steam_rate_limit()
                    sleep_time = 5
                    for _ in range(10):
                        proxy = get_next_proxy()
                        try:
                            response = requests.get(url, proxies=proxy, timeout=10)
                            if response.status_code == 200:
                                logging.info("Successfully fetched data.")
                                break
                        except requests.exceptions.ProxyError:
                            logging.warning(f"Proxy error with {proxy}, trying next proxy.")
                        except requests.exceptions.ConnectTimeout:
                            logging.warning(f"Timeout with proxy {proxy}, trying next proxy.")
                        except Exception as e:
                            logging.error(f"Other error: {e}")
                        time.sleep(sleep_time)
                        sleep_time += 5
                    if response.status_code != 200:
                        raise ValueError(f"Failed to fetch data from {url} after 5 retries")

                    listings = response_parser(response)
                    if not listings:
                        logging.info("No more listings found.")
                        break  # Exit loop if no more listings are found

                    for listing in listings:
                        listing_id = listing['listing_id']
                        price_cents = int(listing['price'])
                        price_dollars = price_cents / 100

                        if not should_process_listing(listing_id, connection):
                            continue

                        for _ in range(5):
                            paint_seed = fetch_paint_seed(listing['inspection_link'])
                            if paint_seed is not None:
                                break
                            time.sleep(60)
                        if paint_seed is None:
                            raise ValueError("Paint Seed is None after 5 retries")

                        logging.info(
                            f"{listing}")
                        insert_listing_into_db(listing, connection)
                        cursor = connection.cursor()
                        cursor.execute("UPDATE listings SET paint_seed = %s WHERE listing_id = %s",
                                       (paint_seed, listing_id))
                        connection.commit()
                        cursor.close()

                        rank = get_rank(paint_seed)
                        if paint_seed is not None and rank is not None:
                            market_link = construct_market_link('Desert Eagle | Heat Treated', quality)
                            message = (
                                f"Oferta <b>{listing_id}</b> \n"
                                f"Paint Seed: <b>{paint_seed}</b> ({get_rank(paint_seed)}) | Cena: <b>{price_dollars}</b>$\n"
                                f"Jakość: <i><a href=\"{market_link}\">{quality}</a></i> | "
                                f"Inspect link: {listing['inspection_link']}"
                            )
                            if should_send_notification(paint_seed, quality, price_dollars):
                                send_telegram_message(message)

                        time.sleep(fetch_paint_seed_rate_limit())

                    # Move to the next page
                    start += count

            connection.close()
            error_backoff = 30 * 60

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            send_telegram_message(str(e))
            traceback.print_exc()

            # Wait for the error backoff timer before retrying
            logging.info(f"Waiting {error_backoff / 60} minutes before retrying due to error.")
            time.sleep(error_backoff)

            # Increase the backoff timer by 30 minutes for the next potential error
            error_backoff += 30 * 60


class CustomFormatter(logging.Formatter):
    # Define color codes
    RESET = "\x1b[0m"
    COLOR_CODES = {
        logging.DEBUG: "\x1b[36m",  # Cyan
        logging.INFO: "\x1b[32m",  # Green
        logging.WARNING: "\x1b[33m",  # Yellow
        logging.ERROR: "\x1b[31m",  # Red
        logging.CRITICAL: "\x1b[41m",  # Red background
    }

    def format(self, record):
        color_code = self.COLOR_CODES.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color_code}{message}{self.RESET}"


# Set up logging with the custom formatter
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter('%(asctime)s [%(levelname)s]: %(message)s'))
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


steam_last_request_time = 0
def steam_rate_limit():
    # Rate limit: new request every 5 seconds
    global steam_last_request_time
    current_time = time.time()
    elapsed_time = current_time - steam_last_request_time
    if elapsed_time < 0.25:
        sleep_time = 0.25 - elapsed_time
        logging.info(f"Waiting {sleep_time:.2f} seconds before the next Steam API request.")
        time.sleep(sleep_time)
    steam_last_request_time = time.time()


fetch_paint_seed_last_request_time = 0
def fetch_paint_seed_rate_limit():
    global fetch_paint_seed_last_request_time
    current_time = time.time()
    elapsed_time = current_time - fetch_paint_seed_last_request_time
    min_interval = 60 / 30  # 30 requests per minute
    if elapsed_time < min_interval:
        sleep_time = min_interval - elapsed_time
        logging.info(f"Waiting {sleep_time:.2f} seconds before the next local API request.")
        fetch_paint_seed_last_request_time = current_time + sleep_time
        return sleep_time
    else:
        fetch_paint_seed_last_request_time = current_time
        return 0


def fetch_paint_seed(inspection_link):
    try:
        encoded_link = urllib.parse.quote(inspection_link, safe='')
        api_url = f"http://localhost:80/?url={encoded_link}"
        response = requests.get(api_url)
        if response.status_code != 200:
            logging.error(f"Error fetching paint_seed for {inspection_link}")
            return None

        data = response.json()
        # Return only the paint_seed from the response if available
        if 'iteminfo' in data and 'paintseed' in data['iteminfo']:
            return data['iteminfo']['paintseed']
        else:
            logging.error(f"No paint_seed found for {inspection_link}")
            return None

    except Exception as e:
        logging.error(f"Error in fetch_paint_seed: {e}")
        return None


async def send_telegram_message_async(message):
    try:
        bot = Bot(token=bot_token)
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=False
        )
    except Exception as e:
        logging.error(f"Error sending message: {e}")


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


def construct_market_link(item_name, quality):
    base_url = "https://steamcommunity.com/market/listings/730/"
    item_name_with_quality = f"{item_name} ({quality})"
    item_name_encoded = urllib.parse.quote(item_name_with_quality, safe='')
    full_url = f"{base_url}{item_name_encoded}"
    return full_url


def get_proxies():
    headers = {
        "Authorization": f"Token {webshare_proxy_api_key}"
    }
    response = requests.get("https://proxy.webshare.io/api/proxy/list/", headers=headers)

    if response.status_code == 200:
        proxy_data = response.json()
        proxies_list = []
        for proxy in proxy_data['results']:
            proxy_format = {
                'https': f"socks5://{proxy['proxy_address']}:{proxy['ports']['socks5']}"
            }
            proxies_list.append(proxy_format)
        return proxies_list
    else:
        logging.error(f"Error fetching proxies: {response.status_code}")
        return []


current_proxies = get_proxies()


def update_proxies():
    global current_proxies
    current_proxies = get_proxies()
    while True:
        current_proxies = get_proxies()
        logging.info("Proxy list updated.")
        time.sleep(30 * 60)  # Update every 30 minutes


def should_send_notification(paint_seed, quality, price):
    rank = get_rank(paint_seed)
    if rank is None:
        return False  # Do not send notification for paint seeds not in any rank
    suggested_price = get_suggested_price(rank, quality)
    if suggested_price is None:
        return False  # Invalid quality or rank
    return price <= suggested_price


def get_rank(paint_seed):
    rank0 = [490, 148, 69, 704]
    rank1 = [16, 48, 66, 67, 96, 111, 117, 159, 259, 263, 273, 297, 308, 321, 324, 341, 347, 461, 482, 517, 530, 567, 587, 674, 695, 723, 764, 772, 781, 790, 792, 843, 880, 885, 904, 948, 990]
    rank2 = [109, 116, 134, 158, 168, 225, 338, 354, 356, 365, 370, 386, 406, 426, 433, 441, 483, 537, 542, 592, 607, 611, 651, 668, 673, 696, 730, 743, 820, 846, 856, 857, 870, 876, 878, 882, 898, 900, 925, 942, 946, 951, 953, 970, 998]
    if paint_seed in rank0:
        return 0
    elif paint_seed in rank1:
        return 1
    elif paint_seed in rank2:
        return 2
    else:
        return None  # Not in any rank


def get_suggested_price(rank, quality):
    suggested_prices = {
        0: {'Factory New': 500, 'Minimal Wear': 250, 'Field-Tested': 200, 'Well-Worn': 150, 'Battle-Scarred': 100},
        1: {'Factory New': 100, 'Minimal Wear': 80, 'Field-Tested': 70, 'Well-Worn': 60, 'Battle-Scarred': 50},
        2: {'Factory New': 60, 'Minimal Wear': 50, 'Field-Tested': 40, 'Well-Worn': 30, 'Battle-Scarred': 20}
    }
    price = suggested_prices.get(rank, {}).get(quality)
    if price is None:
        logging.warning(f"No suggested price found for rank {rank} and quality {quality}")
    return price


proxy_index = 0
def get_next_proxy():
    global proxy_index
    # Ensure proxies are available
    if not current_proxies:
        logging.error("No proxies available.")
        return None

    # Get the current proxy and increment the index
    proxy = current_proxies[proxy_index]

    # Increment index, and reset if we reach the end of the proxy list
    proxy_index = (proxy_index + 1) % len(current_proxies)

    return proxy


if __name__ == "__main__":
    threading.Thread(target=update_proxies, daemon=True).start()
    main()

