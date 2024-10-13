import requests
from main import fetch_paint_seed
from request_tools import *


url = gen_market_link(1, 10)
response = requests.get(url)

print(url)
#print(response.json())


#listings = responce_parser(response)
#print(listings[0]['inspection_link'])
#x = fetch_paint_seed(listings[0]['inspection_link'])
#print(x)
