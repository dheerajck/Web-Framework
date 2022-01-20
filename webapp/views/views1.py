from ..utils.template_handlers import render_template

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


from ..utils.session_handler import get_username_from_environ


def dashboard_view(environ, **kwargs):

    from pprint import pprint

    username = get_username_from_environ(environ)
    # pprint(environ)

    # return render_template("dashboard.html", context={}), start_response_headers
    return render_template("dashboard.html", context={"username": username}), start_response_headers


def session(environ, **kwargs):
    from pprint import pprint

    pprint(environ)
    print("session view")

    html_to_render = render_template("session_test.html", context={})
    html_to_render += f"<h1>{environ.get('HTTP_COOKIE')}"

    return html_to_render, start_response_headers


def view_403(environ, **kwargs):
    return render_template("HTTP403.html", context={}), start_response_headers


def view_404(environ, **kwargs):
    return render_template("HTTP404.html", context={}), start_response_headers
