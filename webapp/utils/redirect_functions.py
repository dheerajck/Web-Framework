def redirect_view(status, url_to_redirect):

    response_headers = [
        ('Location', url_to_redirect),
    ]
    # this dict should contain status and al headers separately
    start_response_headers_dict = {'status': status, 'response_headers': response_headers}
    return start_response_headers_dict
