import secrets
from datetime import datetime, timedelta
from ..orm.models import Session
import psycopg2
from zoneinfo import ZoneInfo

from ..orm.models import User


timezone = ZoneInfo(key='Asia/Kolkata')


def create_session_key():
    return secrets.token_hex(16)


def create_random_link():
    return secrets.token_urlsafe(16)


def create_cookie_header(cookie_name, cookie_value, days=1):
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
            first_header: tuple = create_cookie_header("session_key", session_id)
            # second_header: tuple = create_cookie_header("user_id", userid) might result in security issue

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
    length_of_db_response = len(curent_session_object)
    if length_of_db_response == 0:
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
        # the return value of  this fuunction is changed to dict from None
        #  as a precaution to make everything independent
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
def get_user_from_environ(environ, **kwargs):
    '''
    kwargs accepted instead of args since its more clear for function call
    same value is passed for key and value of kwarg here

    '''

    assert len(kwargs) < 2, "only one keypair is needed maximum"

    SESSION_KEY_NAME = "session_key"

    if len(kwargs) == 0:
        users_value_asked = ["user_id"]
    else:
        # get first_key
        users_value_asked = [next(iter(kwargs.keys()))]

    cookie_string = environ.get('HTTP_COOKIE')
    cookie_dict = get_cookie_dict(cookie_string)

    session_key_value = cookie_dict.get(SESSION_KEY_NAME)

    curent_session_object = Session.objects.select(users_value_asked, {'session_key': session_key_value})

    # because fetchmany returns iterable, fetchone returns one value
    curent_session_object = curent_session_object[0]

    return curent_session_object.user_id


# to depreciate
def get_username_from_environ(environ):
    user_id = get_user_from_environ(environ)
    return User.objects.select_one(['username'], {"id": user_id})[0]


def get_user_details_from_id(user_id, field: list = ["username"]):
    return User.objects.select_one(field, {"id": user_id})


def get_user_details_from_environ(environ, field: list = ["username"]):
    user_id = get_user_from_environ(environ)
    return User.objects.select_one(field, {"id": user_id})
