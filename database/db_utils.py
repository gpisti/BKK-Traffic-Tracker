import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


def get_connection(dbname=DB_NAME):
    """
    Establishes a connection to a PostgreSQL database using the provided or default
    configuration parameters.

    Parameters:
        dbname (str): The name of the database to connect to. Defaults to the value
                    specified in the configuration file.

    Returns:
        connection: A connection object if the connection is successful, otherwise
                    None if an error occurs during the connection attempt.

    Raises:
        Prints an error message if the connection to the database fails.
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
