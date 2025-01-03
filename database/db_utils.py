import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


def get_connection(dbname=DB_NAME):
    """
    Creates and returns a connection to the specified PostgreSQL database.
    """
    try:
        connection = psycopg2.connect(
            dbname=dbname,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        connection.autocommit = True
        return connection
    except Exception as e:
        print(f"Error while connecting to the database {dbname}: {e}")
        return None
