import psycopg2
from secrets import db_secrets


def init_db(connection):
    cursor = connection.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS listings (
        listing_id BIGINT PRIMARY KEY,
        asset_id BIGINT,
        price DECIMAL,
        inspection_link VARCHAR(255),
        paint_seed BIGINT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()


if __name__ == "__main__":
    connection = psycopg2.connect(**db_secrets)
    init_db(connection)
