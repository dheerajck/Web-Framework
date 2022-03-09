from ..utils.template_handlers import render_template
from ..utils.session_handler import get_username_from_environ

import json


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
    # print("session view")
    html_to_render = render_template("session_test.html", context={})
    html_to_render += f"<h1>{environ.get('HTTP_COOKIE')}"

    return html_to_render, start_response_headers


def api_view_403(environ, **kwargs):
    status = "403 Forbidden"
    # message = {"message": "Forbidden"}
    # response_body = {'message': message, 'status': status}
    message = "Forbidden"
    response_body = {'message': message, 'status': status}
    response_body = json.dumps(response_body, indent=4)

    # response_headers = [('Content-type', 'application/json')]
    # response_headers.append(('Content-length', str(len(response_body))))

    response_headers = [('Content-type', 'application/json'), ('Content-length', str(len(response_body)))]

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


def success_api_response(message, status_code="200 OK"):
    response_headers = [
        ('Content-type', 'application/json'),
    ]

    response_body = {'message': message, 'status': status_code}
    response_body = json.dumps(response_body, indent=4)

    response_headers.append(('Content-length', str(len(response_body))))
    start_response_headers: dict = {'status': status_code, 'response_headers': response_headers}
    return response_body, start_response_headers


def error_api_response_codes(status, message):
    status = status
    response_headers = [
        ("Content-type", "application/json"),
    ]

    response_body = {"message": message, "status": status}
    response_body = json.dumps(response_body, indent=4)

    response_headers.append(("Content-length", str(len(response_body))))
    start_response_headers: dict = {
        "status": status,
        "response_headers": response_headers,
    }
    return response_body, start_response_headers
