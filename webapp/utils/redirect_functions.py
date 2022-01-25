def redirect_view(status, url_to_redirect):

    response_headers = [
        ('Location', url_to_redirect),
    ]
    # this dict should contain status and al headers separately
    # add response body response later, redirect doesnt need any response body from users in normal case
    start_response_headers_dict = {'status': status, 'response_headers': response_headers}
    return start_response_headers_dict


def redirect_view_with_response_body(status, url_to_redirect):

    response_headers = [
        ('Location', url_to_redirect),
    ]
    # this dict should contain status and al headers separately
    # add response body response later, redirect doesnt need any response body from users in normal case
    start_response_headers_dict = {'status': status, 'response_headers': response_headers}
    response_body = ''
    return response_body, start_response_headers_dict

def redirect_to_dashboard_module(response_body=''):
    url_to_redirect = '/dashboard/'
    status = '302 FOUND'
    response_body = ''
    start_response_headers_dict = redirect_view(status, url_to_redirect)
    return response_body, start_response_headers_dict


def redirect_to_login_module(response_body=''):
    # http_host = environ.get('HTTP_HOST')
    # print(http_host)
    url_to_redirect = '/login/'  # url_to_redirect = 'login/' made the redirection to  http://localhost:8000/authentication/login/ which is not correct
    status = '302 FOUND'

    # url_to_redirect = 'http://localhost:8000/login/'

    status = '302 FOUND'
    start_response_headers: dict = redirect_view(status, url_to_redirect)

    return response_body, start_response_headers
