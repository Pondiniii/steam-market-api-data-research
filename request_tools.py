import requests
import json

def gen_market_link(start, count, quality):
    return f"https://steamcommunity.com/market/listings/730/Desert%20Eagle%20%7C%20Heat%20Treated%20%28{quality}%29/render?start={start}&count={count}&currency=1&format=json"


def responce_parser(response):
    response = response.json()
    listing_info = response['listinginfo']
    listings = []

    for i in range(len(listing_info)):
        listing_id = list(listing_info.keys())[i]
        asset_id = listing_info[listing_id]['asset']['id']
        
        # Wyciągnij samą cenę z listing_info
        price = listing_info[listing_id].get('converted_price', None)
        if price is None:
            print(f"Brak 'converted_price' dla listing_id: {listing_id}")
            continue
        
        inspection_link = listing_info[listing_id]['asset']['market_actions'][0]['link']
        
        listing = {
            'listing_id': listing_id,
            'asset_id': asset_id,
            'price': price,  # Tutaj teraz mamy liczbę, a nie słownik
            'inspection_link': inspection_link.replace('%listingid%', listing_id).replace('%assetid%', asset_id)
        }
        
        listings.append(listing)

    return listings


if __name__ == "__main__":
    url = gen_market_link(0, 10)
    print(url)
    response = requests.get(url)
    with open('response-rate-limit.json', 'w') as file:
        json.dump(response.json(), file, indent=4)
    print(response.json())
    #print(response['total_count']) 
    listings = responce_parser(response)
    print(listings)
