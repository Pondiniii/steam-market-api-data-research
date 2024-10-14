import psycopg2
from secrets import db_secrets 



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


def insert_listing_into_db(listing, connection):
    listing_id = listing['listing_id']
    asset_id = listing['asset_id']
    price = listing['price']
    inspection_link = listing['inspection_link']
    paint_seed = None  # Initialize with None, to be updated later

    cursor = connection.cursor()

    query = """
    INSERT INTO listings (listing_id, asset_id, price, inspection_link, paint_seed)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (listing_id) DO NOTHING
    """
    cursor.execute(query, (listing_id, asset_id, price, inspection_link, paint_seed))
    connection.commit()

    cursor.close()
    print(f"Inserted or skipped existing listing: {listing_id}")


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
