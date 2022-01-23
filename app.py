from wsgiref.simple_server import make_server
from webapp.url_config import url_handler, url_strip

from webapp.utils.session_handler import get_cookie_dict

from webapp.utils.redirect_functions import redirect_to_login_module
from webapp.utils.session_handler import check_validity_of_session_id

from webapp.clean_print_function.print_enable_and_disable_function import enablePrint, blockPrint

# assert False, "merge this branch and create new branch"
# assert False, "Implement url / strip always" done url_config.url_strip()
# IMPLEMENT MIDDLEWARE


###############################################

# url resolver

###############################################


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

    # path = environ.get('PATH_INFO')
    # # print("newone")
    # print(path)

    # print(environ['HTTP_COOKIE'], type(environ['HTTP_COOKIE']))

    # if path.startswith('/'):
    #     path = path[1:]

    # if path.endswith('/'):
    #     path = path[:-1]

    path = environ.get('PATH_INFO')
    path = url_strip(path)

    # url resolve
    view, kwargs_to_views = url_handler(path)

    # disabling named paramater for now, dont use this now  # html_to_render = response_body = view(environ, **kwargs_to_views)
    # use this instead
    # html_to_render = response_body = view(environ, a=121212)

    start_response_headers: dict = {}

    # calling view
    # also passing dict as key word argument, {'key':value} key=value

    from pprint import pprint

    print("kwargs passing to view")
    pprint(kwargs_to_views)
    html_response_body, start_response_headers = view(environ, **kwargs_to_views)

    # print(path, view)

    # avoided to prevent issue with file downlaod
    # add a new assertion to only allow file download
    # assert type(html_response_body) == str and type(start_response_headers) == dict

    status_basic = '200 OK'
    status = start_response_headers.get('status', status_basic)

    response_header_basic = [
        ('Content-type', 'text/html'),
        ('Content-length', str(len(html_response_body))),
    ]

    response_headers = start_response_headers.get('response_headers', response_header_basic)

    start_response(status, response_headers)
    print(
        "\n\n\n\n________________________________________ COMPLETED ONE REQUEST RESPONSE________________________________________________\n\n\n\n"
    )
    # print(html_response_body)
    # assert isinstance(html_response_body, str), "html response is not string"
    if type(html_response_body) == str:
        html_response_body = html_response_body.encode('utf-8')

    return [html_response_body]


# gunicorn
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
        # blockPrint()
        # enablePrint()
        # print("Middleware starts")

        # print("yo")
        print()
        print("path", environ.get('PATH_INFO'))
        # print(environ.get('HTTP_COOKIE'))
        # a = input()

        # here request from web server is tweeked
        SESSION_KEY_NAME = "session_key"

        path = environ.get('PATH_INFO')
        print(1, path)
        path = url_strip(path)
        print(path)

        # path of static files will be like this
        # path_starting = path.split('/')[0]
        # print("check")
        print(path)
        # static/login.css = > login/static/login.css    /static/login.css = > static/login.css
        # print(path.startswith('login/static/login'))
        cookie_string = environ.get('HTTP_COOKIE')
        if path == "login" or path == "authentication" or path.startswith('static/login'):
            print("so user needs to Sign in to site")
            wrapped_app_response: list = self.wrapped_app(environ, start_response)
            return iter(wrapped_app_response)

        # assert cookie_string is None, "No cookies"
        # no cookies ?? redirect to login page
        # get our apps session_id from cookies
        cookie_dict = get_cookie_dict(cookie_string)  # returns None, NOW RETURNS EMPTY DICT
        session_key_value = cookie_dict.get(SESSION_KEY_NAME)
        # OR do shortcut circuiting so check_validity_of_session_id(session_key_value)
        # will be evaluated onlny if session_key_value is not None
        if session_key_value is None or check_validity_of_session_id(session_key_value) is False:
            response_body, start_response_headers = redirect_to_login_module()
            status = start_response_headers['status']
            response_headers = start_response_headers['response_headers']

            print()
            print()
            print(response_headers)
            start_response(status, response_headers)
            print(
                "\n\n\n\n________________________________________ COMPLETED ONE REQUEST RESPONSE________________________________________________\n\n\n\n"
            )
            return iter([response_body.encode('utf-8')])

        wrapped_app_response = self.wrapped_app(environ, start_response)
        # tweeking response, we can also tweek request
        return iter(wrapped_app_response)


if __name__ == "__main__":

    # make user post, then session middleware

    server = make_server('localhost', 8000, app=SessionMiddleware)
    # server = make_server('localhost', 8000, app=application)
    # adding middleware
    # server = make_server('localhost', 8000, app=Reverse_middleware(application))

    # gunicorn server:SessionMiddleware --reload
    # gunicorn --workers=2 app:SessionMiddleware --reload
    print('Server started')
    server.serve_forever()
