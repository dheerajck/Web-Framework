from wsgiref.simple_server import make_server
from url_config import url_handler

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


###############################################

# url resolver

###############################################


def application(environ, start_response):

    path = environ.get('PATH_INFO')

    if path.startswith('/'):
        path = path[1:]

    if path.endswith('/'):
        path = path[:-1]

    view, kwargs_to_views = url_handler(path)

    # disabling named paramater for now, dont use this now  # html_to_render = response_body = view(environ, **kwargs_to_views)
    # use this instead
    # html_to_render = response_body = view(environ, a=121212)

    html_to_render = response_body = view(environ)

    status = '200 OK'

    response_headers = [
        ('Content-type', 'text/html'),
        ('Content-length', str(len(response_body))),
    ]

    start_response(status, response_headers)

    return [html_to_render.encode('utf-8')]
    # only one data in the list, PEP 333(3) returned data should be an iterable
    ##  return iter([data.encode('utf-8')]) # FIRST, this should be iterable like FIRST


if __name__ == "__main__":
    server = make_server('localhost', 8000, app=application)
    # adding middle ware
    # server = make_server('localhost', 8000, app=Reverse_middleware(application))
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
