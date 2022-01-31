from wsgiref.simple_server import make_server
from webapp.url_config import url_handler, url_strip

from webapp.utils.session_handler import get_cookie_dict

from webapp.utils.redirect_functions import redirect_to_login_module
from webapp.utils.session_handler import check_validity_of_session_id

from api_handler_module import api_handler


class Reverse_middleware:
    def __init__(self, app):
        self.wrapped_app = app

    def __call__(self, environ, start_response, *args, **kwargs):
        wrapped_app_response = self.wrapped_app(environ, start_response)
        # here tweeking response is done by reversing data from app, we can also tweek request
        return [
            data[::-1] for data in wrapped_app_response
        ]  # this should be iterable like FIRST or yield data will work, yeild "data"


def application(environ, start_response, status=None, response_headers=None):

    path = environ.get("PATH_INFO")
    path = url_strip(path)

    # url resolve
    view, kwargs_to_views = url_handler(path)

    start_response_headers: dict = {}

    # calling view
    html_response_body, start_response_headers = view(environ, **kwargs_to_views)

    status_basic = "200 OK"
    status = start_response_headers.get("status", status_basic)

    response_header_basic = [
        ("Content-type", "text/html"),
        ("Content-length", str(len(html_response_body))),
    ]

    response_headers = start_response_headers.get("response_headers", response_header_basic)
    start_response(status, response_headers)
    print(
        "\n\n\n\n________________________________________ COMPLETED ONE REQUEST RESPONSE________________________________________________\n\n\n\n"
    )

    if type(html_response_body) == str:
        html_response_body = html_response_body.encode("utf-8")

    return [html_response_body]


class SessionMiddleware:
    def __init__(self, environ, start_response, app=application):
        self.environ = environ
        self.start_response = start_response
        self.wrapped_app = app

    def __iter__(self):
        environ = self.environ
        start_response = self.start_response

        print()
        print("\n\n__________________Middleware starts_________________\n\n")

        SESSION_KEY_NAME = "session_key"

        path = environ.get("PATH_INFO")
        path = url_strip(path)

        if path.startswith("api"):
            api_login = api_handler(path=path, environ=environ, start_response=start_response)
            return api_login

        # _________________________API HANDLER STOP________________________________

        cookie_string = environ.get("HTTP_COOKIE")
        if path == "login" or path == "authentication" or path.startswith("static/login"):
            # "so user needs to Sign in to site"
            wrapped_app_response: list = self.wrapped_app(environ, start_response)
            return iter(wrapped_app_response)

        cookie_dict = get_cookie_dict(cookie_string)
        session_key_value = cookie_dict.get(SESSION_KEY_NAME)

        if session_key_value is None or check_validity_of_session_id(session_key_value) is False:
            response_body, start_response_headers = redirect_to_login_module()
            status = start_response_headers["status"]
            response_headers = start_response_headers["response_headers"]

            start_response(status, response_headers)
            print(
                "\n\n\n\n________________________________________ COMPLETED ONE REQUEST RESPONSE________________________________________________\n\n\n\n"
            )

            return iter([response_body.encode("utf-8")])

        # tweeking response to the webserver, we can also tweek request
        wrapped_app_response = self.wrapped_app(environ, start_response)

        return iter(wrapped_app_response)


if __name__ == "__main__":
    server = make_server("localhost", 8000, app=SessionMiddleware)
    print("Server started")
    server.serve_forever()
