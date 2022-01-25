from ..utils.post_form_handler import form_with_file_parsing
from ..utils.authentication_functions import authentication_user

from ..utils.session_handler import create_session_id_header, get_cookie_dict, delete_session_id

import json


def login_api_view(environ, **kwargs):
    status = "200 OK"
    response_headers = [
        ('Content-type', 'application/json'),
    ]

    if environ['REQUEST_METHOD'].upper() != 'POST':

        response_body = ''
        status = "405 Method Not Allowed"
        response_headers.append(('Allow', ('POST')))
        response_headers.append(('Content-length', str(len(response_body))))
        start_response_headers: dict = {'status': status, 'response_headers': response_headers}
        return response_body, start_response_headers

    form_field_storage = form_with_file_parsing(environ)

    username = form_field_storage.getvalue('username')
    password = form_field_storage.getvalue('password')
    print(username, password)
    if type(username) == str and type(password) == str:
        pass
    else:
        pass

    # whycalled two times
    # print(authentication_user(username, password))
    authentication_response = authentication_user(username, password)

    if not authentication_response:

        status = "401 Unauthorized"
        response_body = {'message': 'Invalid Credentials', 'status': status}
        response_body = json.dumps(response_body)
        response_headers.append(('Content-length', str(len(response_body))))
        start_response_headers: dict = {'status': status, 'response_headers': response_headers}
        # print(start_response_headers)
        print("xzc")

        return response_body, start_response_headers

    else:

        user_id = authentication_response
        # login succesfull
        # create session id, if user already have a session id replace it with new session id
        # set cookie here
        cookie_headers: list = create_session_id_header(user_id)

        status = "200 OK"
        response_body = {'message': 'Successful', 'status': status}
        response_body = json.dumps(response_body)
        response_headers.append(('Content-length', str(len(response_body))))

        start_response_headers: dict = {'status': status, 'response_headers': response_headers}
        current_list_of_response_headers: list = start_response_headers['response_headers']

        current_list_of_response_headers.extend(cookie_headers)

        start_response_headers['response_headers'] = current_list_of_response_headers

        return response_body, start_response_headers


def logout_api_view(environ, **kwargs):

    response_body = ''
    status = "200 OK"
    response_headers = [
        ('Content-type', 'application/json'),
    ]

    if environ['REQUEST_METHOD'].upper() != 'POST':
        status = "405 Method Not Allowed"
        response_headers.append(('Allow', 'post'))
        response_headers.append(('Content-length', str(len(response_body))))
        start_response_headers: dict = {'status': status, 'response_headers': response_headers}
        return response_body, start_response_headers

    SESSION_KEY_NAME = "session_key"
    cookie_string = environ.get('HTTP_COOKIE')
    cookie_dict = get_cookie_dict(cookie_string)

    # session_key_value = cookie_dict.get(SESSION_KEY_NAME)
    if SESSION_KEY_NAME in cookie_dict:
        session_key_value = cookie_dict[SESSION_KEY_NAME]
        delete_session_id(session_key_value)

    status = "200 OK"
    response_body = {'message': 'Successful', 'status': status}
    response_body = json.dumps(response_body)
    response_headers.append(('Content-length', str(len(response_body))))

    start_response_headers: dict = {'status': status, 'response_headers': response_headers}

    return response_body, start_response_headers
