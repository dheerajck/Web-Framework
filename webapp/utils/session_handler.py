from secrets import token_hex
from datetime import datetime, timedelta
from ..orm.models import Session
import psycopg2
from zoneinfo import ZoneInfo


timezone = ZoneInfo(key='Asia/Kolkata')


def create_session_key():
    return token_hex(16)


def create_session_header(cookie_name, cookie_value, days=1):
    # expiry_date = datetime.now() + timedelta(days=days)
    # path = "/"
    max_age = days * 86400

    session_header = ('Set-Cookie', '{}={}; Max-Age={}; Path=/'.format(cookie_name, cookie_value, max_age))
    return session_header


def create_session_id_header(userid, days=1):

    expiry_date = datetime.now(tz=timezone) + timedelta(days=days)
    while True:
        try:
            # print(Session.select({}, {}))
            session_id = create_session_key()
            # to ensure no duplicate session key is created
            Session.objects.insert_or_update_data(
                key=('user_id'), session_key=session_id, expiry_date=expiry_date, user_id=userid
            )
            first_header: tuple = create_session_header("sesion_id", session_id)
            second_header: tuple = create_session_header("user_id", userid)

        except psycopg2.errors.UniqueViolation:
            pass
        else:
            break

    # import os

    # os.system('cls' if os.name == 'nt' else 'clear')
    headers = []

    # headers.extend([first_header, second_header])
    print("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")
    headers.append(first_header)
    print(headers)
    headers.append(second_header)
    print(headers)
    print("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")

    print('inside')
    print(headers)
    return headers
