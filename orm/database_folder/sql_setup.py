import psycopg2
from .config import config
from datetime import datetime


def connect():
    """Connect to the PostgreSQL database server"""
    connection = None

    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')

        connection = psycopg2.connect(**params)
        connection.set_session(autocommit=True)
        print('Connecting to the PostgreSQL database...Successfull', connection)

        # create a cursor

        return connection

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print()


def disconnect(cursor, connection):
    print('Disconnecting from db...Successfull', connection)
    connection.close()
    cursor.close()


if __name__ == "__main__":
    connection_arguments = connect()

    if connection_arguments is not None:
        connection = connection_arguments
        cursor = connection.cursor()
        disconnect(cursor, connection)
