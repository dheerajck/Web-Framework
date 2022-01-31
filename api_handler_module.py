from webapp.utils.session_handler import get_cookie_dict
from webapp.url_config import url_handler, url_strip
from webapp.utils.session_handler import check_validity_of_session_id

import json


def api_application(environ, start_response, status=None, response_headers=None):

    # response_body = {'message': 'message', 'status': 'status_code}

    html_response_body = ''
    path = environ.get('PATH_INFO')
    path = url_strip(path)

    # url resolve
    view, kwargs_to_views = url_handler(path)

    start_response_headers: dict = {}

    print("kwargs passing to view")
    print(kwargs_to_views)
    html_response_body, start_response_headers = view(environ, **kwargs_to_views)

    status_basic = '200 OK'
    status = start_response_headers.get('status', status_basic)

    # api views should have response headers always set to avoid t=using this response headers
    response_header_basic = [
        ('Content-type', 'application/json'),
        ('Content-length', str(len(html_response_body))),
    ]

    response_headers = start_response_headers.get('response_headers', response_header_basic)

    start_response(status, response_headers)
    print(
        "\n\n\n\n________________________________________ COMPLETED ONE REQUEST RESPONSE________________________________________________\n\n\n\n"
    )

    if type(html_response_body) == str:
        html_response_body = html_response_body.encode('utf-8')

    return [html_response_body]


def api_handler(path, environ, start_response):
    print("API HANDLING")

    wrapped_app = api_application
    status = "200 OK"
    response_headers = [
        ('Content-type', 'application/json'),
    ]

    cookie_string = environ.get('HTTP_COOKIE')
    SESSION_KEY_NAME = "session_key"

    if path == "api/login" or path == "api/logout" or path.startswith('static/login'):
        wrapped_app_response: list = wrapped_app(environ, start_response)
        return iter(wrapped_app_response)

    cookie_dict = get_cookie_dict(cookie_string)
    session_key_value = cookie_dict.get(SESSION_KEY_NAME)

    if session_key_value is None or check_validity_of_session_id(session_key_value) is False:
        status = "401 Unauthorized"
        response_body = {'message': 'Invalid Credentials', 'status': status}

        response_body = json.dumps(response_body)
        response_headers.append(('Content-length', str(len(response_body))))
        start_response_headers: dict = {'status': status, 'response_headers': response_headers}
        print(start_response_headers)

        print(
            "\n\n\n\n________________________________________ COMPLETED ONE REQUEST RESPONSE________________________________________________\n\n\n\n"
        )
        # start response should be called before returning anything to webserver and this is important
        start_response(status, response_headers)
        return iter([response_body.encode('utf-8')])

    wrapped_app_response = wrapped_app(environ, start_response)
    return iter(wrapped_app_response)
