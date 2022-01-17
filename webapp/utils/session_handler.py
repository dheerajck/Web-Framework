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
    # session_header = ('Set-Cookie', '{}={}; Max-Age={};'.format(cookie_name, cookie_value, max_age))
    # default path should be given or the session wont be returned

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
            first_header: tuple = create_session_header("session_key", session_id)
            # second_header: tuple = create_session_header("user_id", userid) might result in security issue

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
    # headers.append(second_header)
    print(headers)
    print("\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")

    print('inside')
    print(headers)
    return headers


def delete_session_id(session_id):
    Session.objects.delete(session_key=session_id)
    return None


def check_validity_of_session_id(session_id):
    curent_session_object = Session.objects.select({}, {'session_key': session_id})
    l = len(curent_session_object)
    if l == 0:
        return False

    else:
        curent_session_object = curent_session_object[0]
        current_time = datetime.now(tz=timezone)
        if current_time >= curent_session_object.expiry_date:
            # deleted the expired session id
            delete_session_id(session_id)

            return False
        else:
            return curent_session_object.user_id


def get_cookie_dict(cookie_string):
    if cookie_string is None:
        # precaution to make everything independent of othe
        return {}
    # dont give "; " ";" is enough
    cookies_list = cookie_string.split(";")
    cookie_dict = {}
    for cookie in cookies_list:
        cookie_name, cookie_value = cookie.split("=")
        # 'session_key' and  ' session_key' made issues because of the space
        cookie_name = cookie_name.strip()
        cookie_value = cookie_value.strip()
        cookie_dict[cookie_name] = cookie_value
    return cookie_dict


# replace others using this
def get_user_from_environ(environ):

    SESSION_KEY_NAME = "session_key"

    cookie_string = environ.get('HTTP_COOKIE')
    cookie_dict = get_cookie_dict(cookie_string)

    session_key_value = cookie_dict.get(SESSION_KEY_NAME)

    curent_session_object = Session.objects.select({}, {'session_key': session_key_value})

    # because fetchmany returns iterable, fetchone returns one value
    curent_session_object = curent_session_object[0]

    return curent_session_object.user_id
