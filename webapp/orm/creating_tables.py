from database_folder.sql_setup import connect, disconnect

if __name__ == "__main__":

    # insert into app_users("name", "username", "email", "password")  values('admin_name 2', 'admin 2', 'a@a.a', 'admin');
    connection = connect()
    cursor = connection.cursor()

    # ____________________________________________________________

    # app_users

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

    # mails

    query = """
    CREATE TABLE IF NOT EXISTS mails (
        id SERIAL PRIMARY KEY,
        created_date timestamp with time zone NOT NULL,
        
        sender integer REFERENCES app_users(id) NOT NULL,
        title varchar(100),
        body text NOT NULL,
        archives boolean DEFAULT false,
        attachment varchar(100)
    )
    """

    cursor.execute(query)

    # ____________________________________________________________

    # groups

    query = """
    CREATE TABLE IF NOT EXISTS groups (
        id SERIAL PRIMARY KEY,
        group_mail varchar(50) UNIQUE NOT NULL
    )
    """

    cursor.execute(query)

    # ____________________________________________________________

    # receivers_of_mail

    query = """
    CREATE TABLE IF NOT EXISTS receivers_of_mail (
        id SERIAL PRIMARY KEY,
       
        mail_id integer REFERENCES mails(id) ON DELETE CASCADE UNIQUE NOT NULL,
        receiver_user integer REFERENCES app_users(id),
        receiver_group integer REFERENCES groups(id),
        
        CONSTRAINT one_foreign_key_not_null CHECK (receiver_user is NOT NULL OR receiver_group is NOT NULL)
    )
    """

    cursor.execute(query)

    # ____________________________________________________________

    # draft_mails

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

    # receivers_of_draft_mails

    query = """
    CREATE TABLE IF NOT EXISTS receivers_of_draft_mails (
        id SERIAL PRIMARY KEY,
        
        draft_id integer REFERENCES draft_mails(id) ON DELETE CASCADE UNIQUE NOT NULL,
        receiver_user integer REFERENCES app_users(id),
        receiver_group integer REFERENCES groups(id)
    )
    """

    cursor.execute(query)

    # ____________________________________________________________

    # user_group

    query = """
        CREATE TABLE IF NOT EXISTS user_group (
            id SERIAL PRIMARY KEY,
            user_id integer REFERENCES app_users (id) NOT NULL,
            group_id integer REFERENCES groups (id) NOT NULL
        )
    """

    cursor.execute(query)

    # ____________________________________________________________

    # session

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
