from . import views
from . import api
import re
from .clean_print_function.clean_print import first_clean_print_function

from urllib.parse import unquote, urlparse
from pathlib import PurePosixPath

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
    '^sent-mails$': views.sent_mail_view,
    '^draft-mails$': views.draft_mails_view,
    '^archives$': views.archives_view,
    '^real-time-chat$': views.real_time_chat_view,
    '^real-time-chat/group/([a-zA-Z0-9_])+$': views.chat_view,
    '^real-time-chat/private-chat/[a-zA-Z0-9_-]+$': views.chat_view,
    # 'mail-user-interactions': views.mail_interactiions_view,
    '^mail-user-interactions-inbox/[0-9]+$': views.mail_interactions_view,
    '^mail-user-interactions-sent/[0-9]+$': views.mail_interactions_view,
    '^mail-user-interactions-archive/[0-9]+$': views.mail_interactions_view,
    '^mail-user-interactions-draft/[0-9]+$': views.mail_interactions_view,
    #
    '^draft-mails/edit-draft/[0-9]+$': views.edit_draft_mail_render_view,
    '^draft/edit-draft-mail-post/[0-9]+$': views.edit_draft_mail_post_view,
    #
    '^inbox/forward/[0-9]+$': views.forward_mail_render_view,
    '^sent-mails/forward/[0-9]+$': views.forward_mail_render_view,
    '^archives/forward/[0-9]+$': views.forward_mail_render_view,
    #
    '^inbox/reply/[0-9]+$': views.reply_mail_render_view,
    '^archives/reply/[0-9]+$': views.reply_mail_render_view,
}


URL_DICTIONARY_API = {
    '^api/login$': api.login_api_view,
    '^api/logout$': api.logout_api_view,
    #
    '^api/compose-mail$': api.compose_mail_api_view,
    '^api/inbox$': api.inbox_api_view,
    '^api/sent-mails$': api.sent_mail_api_view,
    '^api/draft-mails$': api.draft_mails_api_view,
    '^api/archives$': api.archives_api_view,
    #
    # different view used to delete mails from each box
    '^api/inbox/delete/[0-9]+$': api.delete_inbox_api_view,
    '^api/sent-mails/delete/[0-9]+$': api.delete_sent_mail_api_view,
    '^api/draft-mails/delete$/[0-9]+': api.delete_draft_mails_api_view,
    '^api/archives/delete/[0-9]+$': api.delete_archives_api_view,
    #
    '^api/archive-mail/[0-9]+$': api.archive_mail_api_view,
    '^api/unarchive-mail/[0-9]+$': api.unarchive_mail_api_view,
    #
    '^api/draft-mails/edit-draft/[0-9]+$': api.edit_draft_mail_api_view,
    #
    # same view used to forward mail from each box
    '^api/inbox/forward/[0-9]+$': api.forward_mail_api_view,
    '^api/sent-mails/forward/[0-9]+$': api.forward_mail_api_view,
    '^api/archives/forward/[0-9]+$': api.forward_mail_api_view,
    # #
    '^api/inbox/reply/[0-9]+$': api.reply_mail_api_view,
    '^api/archives/reply/[0-9]+$': api.reply_mail_api_view,
}


URL_DICTIONARY.update(URL_DICTIONARY_API)


def url_lookup(url_to_check, url_dict_to_check=URL_DICTIONARY):
    print(url_to_check)
    for pattern, value in url_dict_to_check.items():

        if re.search(pattern, url_to_check):
            return value

    return None


def get_url_path(url):
    return PurePosixPath(unquote(urlparse(url).path)).parts


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

    print("\n\n__________________ URL logger __________________\n\n")
    print(f"URL logger, requested url is {request_url}")
    print("\n\n__________________ DONE __________________\n\n")

    static_file_name_or_false_value = check_static_url(request_url)
    if static_file_name_or_false_value:
        # asking for static content
        kwargs = {'file_name': static_file_name_or_false_value}
        return views.serve_static_file, kwargs

    media_file_name_or_false_value = check_media_url(request_url)
    if media_file_name_or_false_value:
        # asking for media files
        kwargs = {'file_name': media_file_name_or_false_value}
        return views.serve_media_file, kwargs

    view_name = url_lookup(request_url)
    kwargs_passing = {}

    # _________________________________________________________________________

    if view_name in [
        views.edit_draft_mail_render_view,
        views.edit_draft_mail_post_view,
    ]:
        url_split = request_url.split('/')

        url_message_id = int(url_split[-1])
        kwargs_passing = {"mail_id": url_message_id}

    # _________________________________________________________________________

    if view_name is views.forward_mail_render_view or view_name is views.reply_mail_render_view:

        url_split = request_url.split("/")
        kwargs_passing = {"mail_id": int(url_split[-1]), "forward_from": url_split[0], "action_to_do": url_split[1]}

    # __________________________________________________________________________

    if view_name is views.mail_interactions_view:
        url_split = request_url.split('/')

        url_without_message_id: str = "/".join(url_split[:-1])

        url_action = url_without_message_id.split("-")[-1]
        url_message_id = int(url_split[-1])

        kwargs_passing = {"mail_id": url_message_id, "page": url_action}

    # _________________________________________________________________________

    if view_name is views.chat_view:
        kwargs_passing = {"chat_link": request_url.split('/')[-1]}

    first_clean_print_function(f"{request_url} ================> {view_name}")

    if view_name is None:
        print("not match of url view found here")
        if not request_url.startswith('api/'):
            view_name = views.view_404
            kwargs_passing = {}

    # ______________________________________________________________

    if view_name is None:
        print(request_url)
        if request_url.startswith('api/'):
            view_name = api.api_view_404
            kwargs_passing = {}

    if view_name in [
        api.delete_inbox_api_view,
        api.delete_sent_mail_api_view,
        api.delete_draft_mails_api_view,
        api.delete_archives_api_view,
    ]:
        parsing_url = get_url_path(request_url)

        box = parsing_url[1]
        action = parsing_url[2]
        # mail id should be int
        mail_id: int = int(parsing_url[3])
        kwargs_passing = {"box": box, "action": action, "mail_id": mail_id}

    if view_name in [api.archive_mail_api_view, api.unarchive_mail_api_view]:
        parsing_url = get_url_path(request_url)
        mail_id: int = int(parsing_url[-1])
        kwargs_passing = {"mail_id": mail_id}

    if view_name is api.edit_draft_mail_api_view:
        parsing_url = get_url_path(request_url)
        mail_id: int = int(parsing_url[-1])
        kwargs_passing = {"mail_id": mail_id}

    if view_name in [api.forward_mail_api_view, api.reply_mail_api_view]:
        parsing_url = get_url_path(request_url)
        mail_id: int = int(parsing_url[-1])
        box = parsing_url[1]
        kwargs_passing = {"mail_id": mail_id, "box": box}

    return view_name, kwargs_passing


if __name__ == "__main__":
    print(1)
