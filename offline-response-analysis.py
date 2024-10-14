import json


with open('response.json', 'r') as file:
    response = json.load(file)

print(response['total_count'])
#listing_info = response['listinginfo']
#print(listing_info)
#print(len(listing_info))
