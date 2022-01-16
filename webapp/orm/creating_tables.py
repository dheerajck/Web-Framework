from database_folder.sql_setup import connect, disconnect

if __name__ == "__main__":
    connection = connect()
    cursor = connection.cursor()

    # ____________________________________________________________

    query = """
        CREATE TABLE IF NOT EXISTS app_users (
            id SERIAL PRIMARY KEY,
            name varchar(50),
            username varchar(50) UNIQUE NOT NULL,
            email varchar(50) UNIQUE NOT NULL,
            password varchar(100) NOT NULL
        )
    """

    cursor.execute(query)

    # ____________________________________________________________

    query = """
    CREATE TABLE IF NOT EXISTS mails (
        id SERIAL PRIMARY KEY,
        created_date timestamp with time zone NOT NULL,
        
        sender integer REFERENCES app_users(id) NOT NULL,
        title varchar(100),
        body text NOT NULL,
        archives boolean DEFAULT true,
        attachment varchar(100)
    )
    """

    cursor.execute(query)

    # ____________________________________________________________

    query = """
    CREATE TABLE IF NOT EXISTS receivers_of_mail (
        id SERIAL PRIMARY KEY,
       
        mail_id integer REFERENCES mails(id) UNIQUE NOT NULL,
        receiver integer REFERENCES app_users(id) NOT NULL
    )
    """

    cursor.execute(query)

    # ____________________________________________________________

    query = """
    CREATE TABLE IF NOT EXISTS draft_mails (
        id SERIAL PRIMARY KEY,
        created_date timestamp with time zone,
        
        sender integer REFERENCES app_users(id),
        title varchar(100),
        body text,
        archives boolean DEFAULT true,
        attachment varchar(100)
    )
    """

    cursor.execute(query)

    # ____________________________________________________________

    query = """
    CREATE TABLE IF NOT EXISTS groups (
        id SERIAL PRIMARY KEY,
        group_mail varchar(50) UNIQUE NOT NULL
    )
    """

    cursor.execute(query)

    # ____________________________________________________________

    query = """
        CREATE TABLE IF NOT EXISTS user_group (
            id SERIAL PRIMARY KEY,
            user_id integer REFERENCES app_users (id) NOT NULL,
            group_id integer REFERENCES groups (id) NOT NULL
        )
    """

    cursor.execute(query)

    # ____________________________________________________________

    query = """
        CREATE TABLE IF NOT EXISTS session (
            id SERIAL PRIMARY KEY,
            session_key varchar(100) UNIQUE NOT NULL,
            expiry_date timestamp with time zone NOT NULL,
            
            user_id integer REFERENCES app_users (id) UNIQUE NOT NULL
        )
    """

    cursor.execute(query)

    # ____________________________________________________________
