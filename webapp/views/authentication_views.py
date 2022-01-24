from ..utils.template_handlers import render_template
from ..utils.post_form_handler import form_with_file_parsing
from ..utils.authentication_functions import authentication_user
from ..utils.redirect_functions import redirect_view

from ..utils.session_handler import create_session_id_header, get_cookie_dict, delete_session_id
from ..utils.redirect_functions import redirect_to_login_module


start_response_headers: dict = {}


def authenticating_view(environ, **kwargs):

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
        print(f'{cookie_headers=}')

        # http_host_is_not_needed_in_current_case
        # http_host = environ.get('HTTP_HOST')
        # redirect_url_path = '/dashboard/'
        # button = form_field_storage.getvalue('password')
        # if form_field_storage.getvalue('input_pressed') == 'regiser':

        # Launched external handler for 'localhost:8000//dashboard/'.
        # url_to_redirect = f'{http_host}/{redirect_url_path}'

        # important dont strip this "/ at starting is important / at the end is not important"
        url_to_redirect = '/dashboard/'
        status = '302 FOUND'

        start_response_headers: dict = redirect_view(status, url_to_redirect)
        current_list_of_response_headers: list = start_response_headers['response_headers']

        current_list_of_response_headers.extend(cookie_headers)

        start_response_headers['response_headers'] = current_list_of_response_headers

        return response_body, start_response_headers


def login_view(environ, **kwargs):

    print("LOGIN")
    # pprint(environ)

    return render_template("authentication-templates/login-register.html", context={}), start_response_headers


def logout_view(environ, **kwargs):

    SESSION_KEY_NAME = "session_key"

    # pprint(environ)
    # print("yess")
    # print()
    # print(cookie_string := environ.get('HTTP_COOKIE'))
    # print()
    cookie_string = environ.get('HTTP_COOKIE')
    # print("///")
    # print(cookie_string is None)

    # we need to make sure HTTP_COOKIE is not None, so cookie_string is not None should return True to proceed
    # assert cookie_string is not None, "No cookies, then how stayed in the website till now"
    # get our apps session_id from cookies
    cookie_dict = get_cookie_dict(cookie_string)
    # print()
    # print("////////////")
    # print(cookie_dict)

    # session_key_value = cookie_dict.get(SESSION_KEY_NAME)
    # if condition false raise error
    # assert SESSION_KEY_NAME in cookie_dict, "Again asking, No cookies, then how stayed in the website till now"
    # removed assertion and added this check to avoid assertion error and key error if user directly go to logout url for somereason
    if SESSION_KEY_NAME in cookie_dict:
        session_key_value = cookie_dict[SESSION_KEY_NAME]
        delete_session_id(session_key_value)

    return redirect_to_login_module()
