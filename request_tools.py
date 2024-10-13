import requests
import json

def gen_market_link(start, count):
    return f"https://steamcommunity.com/market/listings/730/Desert%20Eagle%20%7C%20Heat%20Treated%20%28Factory%20New%29/render?start={start}&count={count}&currency=1&format=json"


def responce_parser(response):
    response = response.json()
    listing_info = response['listinginfo']
    listings = []

    for i in range(len(listing_info)):
        listing_id = list(listing_info.keys())[i]
        asset_id = listing_info[listing_id]['asset']['id']
        price = listing_info[listing_id]['converted_price']
        inspection_link = listing_info[listing_id]['asset']['market_actions'][0]['link']
        
        listing = {
            'listing_id': listing_id,
            'asset_id': asset_id,
            'price': price,
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
    len(response.json())
    print(response['total_count']) # zwraca ile jest ofert na steam market czyli można podzielić przez 100 = ilość requestów do wykonania 100 to maksymalna ilość danych w response od steam api
    listings = responce_parser(response)
    print(listings)
