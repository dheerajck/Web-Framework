from . import views
from .clean_print_function.clean_print import first_clean_print_function

URL_DICTIONARY = {
    '^$': views.root,
    '^test$': views.test,
    '^login': views.login_view,
    '^dashboard$': views.dashboard_view,
    '^authentication$': views.authenticating_view,
    '^session$': views.session,
    '^logout$': views.logout_view,
    '^dashboard/compose-mail$': views.compose_mail_view,
    '^compose-mail-post-view$': views.compose_mail_post_view,
    '^inbox$': views.inbox_view,
    # '^sent-mails$': views.sent_mail_view,
    # '^draft-mails$': views.draft_mails_view,
    # '^archives$': views.archives_view,
    # '^real-time-chat$': views.real_time_chat_view,
    # '^real-time-chat/group/([a-zA-Z0-9_])+$': views.groups_view,
    # # 'mail-user-interactions': views.mail_interactiions_view,
    # '^mail-user-interactions-inbox/[0-9]+$': views.mail_interactions_view,
    # '^mail-user-interactions-sent/[0-9]+$': views.mail_interactions_view,
    # '^mail-user-interactions-archive/[0-9]+$': views.mail_interactions_view,
    # '^mail-user-interactions-draft/[0-9]+$': views.mail_interactions_view,
}


'''
home/<str:pk>/
for url with kwarg pk

can use regex
'''

import re


def url_lookup(url_to_check, url_dict_to_check=URL_DICTIONARY):
    print(url_to_check)
    for pattern, value in url_dict_to_check.items():
        # print("@@")
        # print()
        # print(pattern, value)
        # print()
        # print("@@")
        if re.search(pattern, url_to_check):
            # print(url_to_check, pattern, value)
            # print("yes")
            return value
    return None


def url_strip(url):
    return url.strip("/")


def check_media_url(request_url):
    checking_url = request_url.split('/')
    if checking_url[0] == 'media' and len(checking_url) == 2:
        return checking_url[1]
    return False


def check_static_url(request_url):
    checking_url = request_url.split('/')
    if checking_url[0] == 'static' and len(checking_url) == 2:
        return checking_url[1]
    return False


def url_handler(request_url):

    print(f"\n\n__________________ URL logger __________________\n\n")
    print(f"URL logger, requested url is {request_url}")
    print(f"\n\n__________________ DONE __________________\n\n")

    static_file_name_or_false_value = check_static_url(request_url)
    if static_file_name_or_false_value:
        # if asking for static content
        kwargs = {'file_name': static_file_name_or_false_value}
        return views.serve_static_file, kwargs

    media_file_name_or_false_value = check_media_url(request_url)
    if media_file_name_or_false_value:
        kwargs = {'file_name': media_file_name_or_false_value}
        return views.serve_media_file, kwargs

    view_name = url_lookup(request_url)
    kwargs_passing = {}
    # print(view_name, views.mail_interactions_view)
    # print(view_name is views.mail_interactions_view)

    # if view_name is views.mail_interactions_view:
    #     print("mail_interaction")
    #     url_split = request_url.split('/')

    #     url_without_message_id: str = "/".join(url_split[:-1])

    #     url_action = url_without_message_id.split("-")[-1]
    #     url_message_id = int(url_split[-1])

    #     kwargs_passing = {"mail_id": url_message_id, "action": url_action}
    #     print(kwargs_passing)

    # if view_name is views.groups_view:
    #     kwargs_passing = {"group_name": request_url.split('/')[-1]}
    #     print(kwargs_passing)
    # Replace using regex
    # done
    # ___________________________________________________
    # if request_url.startswith('mail-user-interactions'):
    #     kwargs = {
    #         "mail_id": int(request_url.split('/')[-1]),
    #     }
    #     if request_url.split('/')[-1] == "mail-user-interactions":
    #         # if no mail id is passed
    #         return views.view_404, {}

    #     return views.mail_interactiions_view, kwargs
    # ___________________________________________________

    # view_name = URL_DICTIONARY.get(request_url, None)
    # view_name = url_lookup(request_url)
    # if not (request_url == 'favicon.ico'):

    first_clean_print_function(f"{request_url} ================> {view_name}")

    if view_name is None:
        print("not here")
        # if url not in url
        return views.view_404, {}

    # add more if needed
    # for the view root, dont send anyother kwargs

    # try regex for url matching and template parsing later dont do this first, important works first

    return view_name, kwargs_passing


if __name__ == "__main__":
    print(1)
