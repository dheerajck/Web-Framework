from ...utils.post_form_handler import form_with_file_parsing
from ...utils.session_handler import get_user_from_environ
from ...utils.template_handlers import render_template

from ..views1 import view_403
from ...utils.redirect_functions import redirect_view

from .inbox_view import get_inbox
from .archived_mail_view import get_archives
from .sent_mail_view import get_send_mails
from .draft_views import get_draft_mails


from ...orm.models import Mails, UserInbox, UserSent


allowed_actions = {
    "inbox": {"archive", "reply", "forward", "delete"},
    "archive": {"unarchive", "reply", "forward", "delete"},
    "sent": {"delete"},
    "draft": {"delete"},
}


def mail_interactions_view(environ, **kwargs):

    response_body = ''
    # redirect_data_response_headers = redirect_view('302 FOUND', '/inbox')

    # user_id = get_user_from_environ(environ)
    mail_id = kwargs["mail_id"]
    page = kwargs["page"]
    print(f"{page}///////////////////////////////////////////////")
    form_field_object = form_with_file_parsing(environ)
    print("test")
    print(form_field_object)
    user_interaction = form_field_object.getvalue('interaction')
    print(user_interaction)
    print(user_interaction)
    # print('///////////////////////////////////////')

    # mail.mail_id in inbox and archive

    # mail.id in sent and draft
    if page == "inbox":
        box_mails = get_inbox(environ)
        box_mails = {mail.mail_id for mail in box_mails}
        redirect_data_response_headers = redirect_view('302 FOUND', '/inbox')

    elif page == "archive":
        box_mails = get_archives(environ)
        print(box_mails)
        print("g6")
        box_mails = {mail.mail_id for mail in box_mails}
        redirect_data_response_headers = redirect_view('302 FOUND', '/archives')

    elif page == "sent":
        box_mails = get_send_mails(environ)
        print("///////////////////////////////////////////////////////////////////////")
        box_mails = {mail.id for mail in box_mails}
        print(box_mails)
        redirect_data_response_headers = redirect_view('302 FOUND', '/sent-mails')

    elif page == "draft":
        box_mails = get_draft_mails(environ)
        box_mails = {mail.id for mail in box_mails}
        print(box_mails)
        redirect_data_response_headers = redirect_view('302 FOUND', '/draft-mails')

    print(box_mails)

    print(user_interaction, page)
    if mail_id not in box_mails or user_interaction not in allowed_actions[page]:
        if mail_id not in box_mails:
            print("mail abscent")
        else:
            print(f'action {user_interaction}not allowed in the page {page}')
        kwargs_passing = {}
        print("no")
        # Access denied
        return view_403(environ, **kwargs_passing)

    print("hi")

    if user_interaction == "archive":
        UserInbox.objects.update({"archived_mail": True}, {"mail_id": mail_id})
    elif user_interaction == "unarchive":
        UserInbox.objects.update({"archived_mail": False}, {"mail_id": mail_id})

    elif user_interaction == "delete":
        # need more checks to clean
        if page in {"inbox", "archive"}:
            UserInbox.objects.update({"deleted": True}, {"mail_id": mail_id})
        elif page in {"sent", "draft"}:
            UserSent.objects.update({"deleted": True}, {"mail_id": mail_id})

    elif user_interaction == "reply":
        pass
    elif user_interaction == "forward":
        pass

    return response_body, redirect_data_response_headers
