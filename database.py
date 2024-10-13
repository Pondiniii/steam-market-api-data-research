import psycopg2
from secrets import db_secrets 




def check_listing_in_db(listing_id, connection):
    cursor = connection.cursor()
    query = "SELECT EXISTS(SELECT 1 FROM listings WHERE listing_id = %s)"
    cursor.execute(query, (listing_id,))
    exists = cursor.fetchone()[0]
    cursor.close()
    return exists


def insert_listing_into_db(listing, connection):
    listing_id = listing['listing_id']
    asset_id = listing['asset_id']
    price = listing['price']
    inspection_link = listing['inspection_link']
    paint_seed = None  # Zainicjuj z None, na późniejsze uzupełnienie

    # Sprawdź czy listing_id istnieje już w bazie
    if not check_listing_in_db(listing_id, connection):
        cursor = connection.cursor()

        query = """
        INSERT INTO listings (listing_id, asset_id, price, inspection_link, paint_seed)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (listing_id, asset_id, price, inspection_link, paint_seed))
        connection.commit()

        cursor.close()
        print(f"Zapisano nowe dane: {listing_id}, {asset_id}, {price}, {inspection_link}")
    else:
        print(f"Dane już istnieją w bazie: {listing_id}")


if __name__ == "__main__":
    connection = psycopg2.connect(**db_secrets)
    listings = [
        {'listing_id': '5383581618464676059', 'asset_id': '39936452179', 'price': 2809, 'inspection_link': 'steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20M5383581618464676059A39936452179D16736084355061401401'},
        {'listing_id': '5372322619400002578', 'asset_id': '39807265519', 'price': 2817, 'inspection_link': 'steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20M5372322619400002578A39807265519D12548944050771766193'},
        {'listing_id': '5400470117071996455', 'asset_id': '39940795986', 'price': 2820, 'inspection_link': 'steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20M5400470117071996455A39940795986D9272454425638473723'}
    ]

    for listing in listings:
        insert_listing_into_db(listing, connection)
    connection.close()
