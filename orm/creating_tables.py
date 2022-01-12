from database_folder.sql_setup import connect, disconnect

if __name__ == "__main__":
    cursor, connection = connect()

    query = """
        CREATE TABLE UserTable (
            id SERIAL PRIMARY KEY,
            name varchar(255) NOT NULL,
            email varchar(255) NOT NULL,
            password varchar(255) NOT NULL
        )
    """

    cursor.execute(query)

    query = """
    CREATE TABLE mails (
        id SERIAL PRIMARY KEY,
        title varchar(255),
        body text NOT NULL,
        attachment varchar(255)
        date timestamp with time zone NOT NULL,

    )
    """

    cursor.execute(query)

    query = """
    CREATE TABLE groups (
        id SERIAL PRIMARY KEY,
        group_mail varchar(255) NOT NULL
    )
"""

    cursor.execute(query)

    query = """
        CREATE TABLE user_group (
            id SERIAL PRIMARY KEY,
            user_id integer REFERENCES UserTable(id),
            group_id integer REFERENCES groups(id)
        )
"""

    cursor.execute(query)
