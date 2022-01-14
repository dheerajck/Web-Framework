from . import views
from .clean_print_function.clean_print import first_clean_print_function

URL_DICTIONARY = {
    '': views.root,
    'test': views.test,
    'login': views.login_view,
    'dashboard': views.dashboard_view,
    'authentication': views.authenticating_view,
    'session': views.session,
}


'''
home/<str:pk>/
for url with kwarg pk

can use regex
'''


def url_handler(request_url):

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
