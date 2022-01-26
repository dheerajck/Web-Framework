from ..utils.template_handlers import render_template
from ..utils.session_handler import get_username_from_environ


start_response_headers: dict = {}

# only using kwargs since args might create unwanted problems and nkeyword arguments will be better its explicit
# changed to named parameters because its better to not accept unwanted keyword argument, this throws cant unpack error so avoiding for now


def root(environ, **kwargs):
    return render_template("root.html", context={}), start_response_headers


def test(environ, **kwargs):
    # from ..clean_print_function.clean_print import first_clean_print_function
    # first_clean_print_function(environ)
    from pprint import pprint

    response_body = {str(key): str(value) for key, value in sorted(environ.items())}
    response_body = '\n'.join(response_body)
    pprint(response_body)

    return render_template("test.html", context={}), start_response_headers


def dashboard_view(environ, **kwargs):

    username = get_username_from_environ(environ)
    # pprint(environ)

    # return render_template("dashboard.html", context={}), start_response_headers
    return render_template("dashboard.html", context={"username": username}), start_response_headers


def session(environ, **kwargs):

    # pprint(environ)
    print("session view")

    html_to_render = render_template("session_test.html", context={})
    html_to_render += f"<h1>{environ.get('HTTP_COOKIE')}"

    return html_to_render, start_response_headers


def api_view_403(environ, **kwargs):
    response_body = ''
    response_headers = [
        ('Content-type', 'application/json'),
    ]

    status = "403 Forbidden"
    response_headers.append(('Content-length', str(len(response_body))))
    start_response_headers: dict = {'status': status, 'response_headers': response_headers}
    return response_body, start_response_headers


def api_view_405(environ, **kwargs):
    response_body = ''
    response_headers = [
        ('Content-type', 'application/json'),
    ]
    allowed_methods: tuple = kwargs.get("allowed")
    allowed_methods: str = ", ".join(allowed_methods)
    
    status = "405 Method Not Allowed"
    response_headers.append(('Allow', allowed_methods))
    response_headers.append(('Content-length', str(len(response_body))))
    start_response_headers: dict = {'status': status, 'response_headers': response_headers}
    return response_body, start_response_headers


def api_view_404(environ, **kwargs):
    response_body = ''
    response_headers = [
        ('Content-type', 'application/json'),
    ]

    status = "404 Not Found"
    response_headers.append(('Content-length', str(len(response_body))))
    start_response_headers: dict = {'status': status, 'response_headers': response_headers}
    return response_body, start_response_headers
