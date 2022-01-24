from database_folder.sql_setup import connect, disconnect

if __name__ == "__main__":

    # insert into app_users("name", "username", "email", "password")  values('admin_name', 'admin', 'admin@admin.com', 'admin');
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

    # groups

    query = """
    CREATE TABLE IF NOT EXISTS groups (
        id SERIAL PRIMARY KEY,
        group_name varchar(50) UNIQUE NOT NULL,
        group_mail varchar(50) UNIQUE NOT NULL
    )
    """

    cursor.execute(query)

    # ____________________________________________________________

    # ____________________________________________________________

    # mails
    # group id will be null if its not a group mail
    query = """
    CREATE TABLE IF NOT EXISTS mails (
        id SERIAL PRIMARY KEY,
        created_date timestamp with time zone NOT NULL,
        draft boolean DEFAULT false,
        title varchar(100),
        body text,
        attachment varchar(100)
    )
    """

    cursor.execute(query)

    # ____________________________________________________________
    # user_sent

    query = """
    CREATE TABLE IF NOT EXISTS user_sent (
        id SERIAL PRIMARY KEY,
        user_id integer REFERENCES app_users(id) ON DELETE CASCADE NOT NULL,
        mail_id integer REFERENCES mails(id) ON DELETE CASCADE UNIQUE NOT NULL,
        deleted boolean DEFAULT false
    )
    """

    cursor.execute(query)

    # ____________________________________________________________

    # user_inbox

    query = """
    CREATE TABLE IF NOT EXISTS user_inbox (
        id SERIAL PRIMARY KEY,
        user_id integer REFERENCES app_users(id) ON DELETE CASCADE NOT NULL,
        mail_id integer REFERENCES mails(id) ON DELETE CASCADE NOT NULL,
        archived_mail boolean DEFAULT false,
        
        group_id integer REFERENCES groups (id),
        deleted boolean DEFAULT false
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

            user_id integer REFERENCES app_users (id) NOT NULL
        )
    """

    cursor.execute(query)

    # ____________________________________________________________

    # user_group

    query = """
        CREATE TABLE IF NOT EXISTS users_private_chat (
            id SERIAL PRIMARY KEY,
            user_id_1 integer REFERENCES app_users (id) NOT NULL,
            user_id_2 integer REFERENCES app_users (id) NOT NULL,
            private_chat_link varchar(100) UNIQUE NOT NULL,
            UNIQUE (user_id_1, user_id_2)
        )
    """

    cursor.execute(query)

    # ____________________________________________________________
