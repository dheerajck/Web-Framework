from ..utils.template_handlers import render_template
from ..utils.post_form_handler import form_with_file_parsing
from ..utils.authentication_functions import authentication_user
from ..utils.redirect_functions import redirect_view

from ..utils.session_handler import create_session_id_header


def redirect_to_login_module(response_body=''):
    # http_host = environ.get('HTTP_HOST')
    # print(http_host)
    url_to_redirect = (
        '/login/'  # url_to_redirect = 'login/' made the redirection to  http://localhost:8000/authentication/login/
    )
    status = '302 FOUND'

    # url_to_redirect = 'http://localhost:8000/login/'
    redirect_url_path = '/login/'

    status = '302 FOUND'
    start_response_headers: dict = redirect_view(status, url_to_redirect)

    return response_body, start_response_headers


def authenticating_view(environ, **kwargs):
    from ..orm.models import User

    response_body = ''  # beccause this is a redirect view

    if environ['REQUEST_METHOD'].upper() != 'POST':

        return redirect_to_login_module()

    form_field_storage = form_with_file_parsing(environ)
    username = form_field_storage.getvalue('username')
    password = form_field_storage.getvalue('password')
    print(username, password)
    # whycalled two times
    # print(authentication_user(username, password))
    authentication_response = authentication_user(username, password)

    if not authentication_response:
        return redirect_to_login_module()

    else:

        user_id = authentication_response
        # login succesfull
        # create session id, if user already have a session id replace it with new session id
        # set cookie here
        cookie_headers: list = create_session_id_header(user_id)
        print(cookie_headers)
        print("||||||||||||||||||||||||||||||\\")
        # http_host_is_not_needed_in_current_case
        # http_host = environ.get('HTTP_HOST')
        # redirect_url_path = '/dashboard/'

        # Launched external handler for 'localhost:8000//dashboard/'.
        # url_to_redirect = f'{http_host}/{redirect_url_path}'
        url_to_redirect = '/dashboard/'
        status = '302 FOUND'

        start_response_headers: dict = redirect_view(status, url_to_redirect)
        start_response_headers["extend"] = cookie_headers
        print()
        print()

        print("{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{")
        print("on view", start_response_headers)

        return response_body, start_response_headers
