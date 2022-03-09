from ..utils.template_handlers import render_template
from ..utils.session_handler import get_username_from_environ


start_response_headers: dict = {}


def root(environ, **kwargs):
    return render_template("root.html", context={}), start_response_headers


def test(environ, **kwargs):

    response_body = {str(key): str(value) for key, value in sorted(environ.items())}
    response_body = '\n'.join(response_body)
    return render_template("test.html", context={}), start_response_headers


def dashboard_view(environ, **kwargs):

    username = get_username_from_environ(environ)
    return render_template("dashboard.html", context={"username": username}), start_response_headers


def session(environ, **kwargs):

    print("session view")
    html_to_render = render_template("session_test.html", context={})
    html_to_render += f"<h1>{environ.get('HTTP_COOKIE')}"
    return html_to_render, start_response_headers


def view_403(environ, **kwargs):
    start_response_headers["status"] = "403 Forbidden"
    return render_template("HTTP403.html", context={}), start_response_headers


def view_404(environ, **kwargs):
    start_response_headers["status"] = "404 Not Found"
    return render_template("HTTP404.html", context={}), start_response_headers
