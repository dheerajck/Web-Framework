from wsgiref.simple_server import make_server
from url_config import url_handler


# use this after class single middleware works well
import functools

CONDITION = True


def session_decorator(condition):
    def decorator_function(function):

        '''
        *args, **kwargs
        '''

        @functools.wraps(function)
        def wrapper(*args):

            if condition:
                global CONDITION
                environ, start_response, status, response_headers = args
                print("Something is happening before the function is called.")
                return_values = function(*args)
                print("Something is happening after the function is called.")
                return return_values
            else:
                return function(*args)

        return wrapper

    return decorator_function


###############################################

# url resolver

###############################################


class Reverse_middleware:
    def __init__(self, app):
        self.wrapped_app = app

    def __call__(self, environ, start_response, *args, **kwargs):
        wrapped_app_response = self.wrapped_app(environ, start_response)
        # tweeking response, we can also tweek request
        return [
            data[::-1] for data in wrapped_app_response
        ]  # this should be iterable like FIRST or yield data will work, yeild "data"


class SessionMiddleware:
    def __init__(self):
        self.wrapped_app = application

    def __call__(self, environ, start_response, *args, **kwargs):
        wrapped_app_response = self.wrapped_app(environ, start_response)
        # tweeking response, we can also tweek request
        return [
            data[::-1] for data in wrapped_app_response
        ]  # this should be iterable like FIRST or yield data will work, yeild "data"


# @session_decorator(CONDITION)
def application(environ, start_response, status=None, response_headers=None):

    path = environ.get('PATH_INFO')

    if path.startswith('/'):
        path = path[1:]

    if path.endswith('/'):
        path = path[:-1]

    view, kwargs_to_views = url_handler(path)

    # disabling named paramater for now, dont use this now  # html_to_render = response_body = view(environ, **kwargs_to_views)
    # use this instead
    # html_to_render = response_body = view(environ, a=121212)

    start_response_headers: dict = {}

    html_response_body, start_response_headers = view(environ)
    #  verifying data receievd from functions
    assert type(html_response_body) == str and type(start_response_headers) == dict

    status_basic = '200 OK'
    status = start_response_headers.get('status', status_basic)

    response_header_basic = [
        ('Content-type', 'text/html'),
        ('Content-length', str(len(html_response_body))),
    ]

    response_headers = start_response_headers.get('response_headers', response_header_basic)

    start_response(status, response_headers)

    return [html_response_body.encode('utf-8')]


if __name__ == "__main__":

    # make user post, then session middleware
    # server = make_server('localhost', 8000, app=SessionMiddleware(application))

    server = make_server('localhost', 8000, app=application)
    # adding middle ware
    # server = make_server('localhost', 8000, app=Reverse_middleware(application))

    # gunicorn server:SessionMiddleware --reload
    print('Server started')
    server.serve_forever()

    """def render_template(template_name, context={}):
    html_string = ''
    with open()...
    html_string=f.read
    return html strign"""

    """path = environ.get("PTH_INFO")if path ==x:
            data = x(y)
            example data = home(environ)
        else path == xy
        data = contact(environ)
        if path.endswith('/') remove this last 
    """

    """view template response now"""

    """functions view template html"""
