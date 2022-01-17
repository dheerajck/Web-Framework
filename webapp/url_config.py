from . import views
from .clean_print_function.clean_print import first_clean_print_function

URL_DICTIONARY = {
    '': views.root,
    'test': views.test,
    'login': views.login_view,
    'dashboard': views.dashboard_view,
    'authentication': views.authenticating_view,
    'session': views.session,
    'logout': views.logout_view,
    'dashboard/compose-mail': views.compose_mail_view,
    'compose-mail-post-view': views.compose_mail_post_view,
}


'''
home/<str:pk>/
for url with kwarg pk

can use regex
'''


def url_strip(url):
    return url.strip("/")


def check_static_url(request_url):
    checking_url = request_url.split('/')
    if checking_url[0] == 'static' and len(checking_url) == 2:
        return checking_url[1]
    return False


def url_handler(request_url):

    print(f"\n\n__________________ URL logger __________________\n\n")
    print("url logger", request_url)
    print(f"\n\n__________________ DONE __________________\n\n")

    static_file_name_or_false_value = check_static_url(request_url)
    if static_file_name_or_false_value:
        # if asking for static content
        kwargs = {'file_name': static_file_name_or_false_value}
        return views.serve_static_file, kwargs

    view_name = URL_DICTIONARY.get(request_url, None)
    if not (request_url == 'favicon.ico'):

        first_clean_print_function(f"{request_url} ================> {view_name}")

    if view_name is None:
        # if url not in url
        return views.view_404, {}

    # add more if needed
    # for the view root, dont send anyother kwargs
    kwargs_passing = {}

    # try regex for url matching and template parsing later dont do this first, important works first

    return view_name, kwargs_passing


if __name__ == "__main__":
    print(1)
