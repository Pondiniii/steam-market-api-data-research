for page in range(max_pages):
    # Update the URL for the current page
    url = gen_market_link(start, count, quality)
    
    # Rate limit to avoid spamming Steam
    steam_rate_limit()
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching data from {url}")
        continue  # Skip to the next page
    
    # Parse the response and process listings
    listings = response_parser(response)
    
    if not listings:
        print("No more listings found.")
        break  # Exit loop if no more listings are found

    should_skip_remaining_pages = False  # Reset flag for each page
    
    # Process each listing
    for listing in listings:
        price_cents = int(listing['price'])
        price_dollars = price_cents / 100  # Convert to dollars

        if price_dollars > 100:
            print(f"Price {price_dollars} exceeds $100, skipping remaining listings and pages for quality {quality}")
            should_skip_remaining_pages = True
            break  # Break out of listing loop

        listing_id = listing['listing_id']
        
        if not should_process_listing(listing_id, connection):
            print(f"Skipping listing {listing_id}, already processed.")
            continue
        
        # Insert the listing into the database
        insert_listing_into_db(listing, connection)
        
        # Fetch paint_seed for this listing
        paint_seed = fetch_paint_seed(listing['inspection_link'])
        if paint_seed == None:
            raise ValueError("Paint Seed is None - check self-hosted API")
        print(f"Paint seed for listing {listing_id} (Quality: {quality}): {paint_seed}")
        
        # Update the database with the fetched paint_seed
        cursor = connection.cursor()
        cursor.execute("UPDATE listings SET paint_seed = %s WHERE listing_id = %s", (paint_seed, listing_id))
        connection.commit()
        cursor.close()
        
        # Send notification if the paint_seed meets criteria
        if paint_seed is not None and meets_criteria(paint_seed):
            if price_dollars > 100:
                print(f"Skipping notification for listing {listing_id} due to price {price_dollars} > $100")
                continue  # Skip sending the notification
            
            # Construct the Steam market link for the listing
            market_link = construct_market_link(item_name, quality)
            
            # Prepare and send the message
            message = (
                f"Oferta <b>{listing_id}</b> \n"
                f"Paint Seed: <b>{paint_seed}</b> | Cena: <b>{price_dollars}</b>$\n"
                f"Jakość: <i><a href=\"{market_link}\">{quality}</a></i> | "
                f"Inspect link: {listing['inspection_link']}"
            )
            print(message)
            send_telegram_message(message)
        
        # Rate limit for paint_seed API
        time.sleep(fetch_paint_seed_rate_limit())
    
    if should_skip_remaining_pages:
        break  # Break out of page loop, proceed to next quality
    
    # Move to the next page
    start += count

