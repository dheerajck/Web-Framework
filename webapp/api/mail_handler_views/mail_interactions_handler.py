from ...utils.post_form_handler import form_with_file_parsing


from .inbox_view import get_inbox
from .archived_mail_view import get_archives
from .sent_mail_view import get_send_mails
from .draft_views import get_draft_mails


from ...orm.models import UserInbox, UserSent

from ..views1 import api_view_403, success_api_response, api_view_405

allowed_actions = {
    "inbox": {"archive", "reply", "forward", "delete"},
    "archive": {"unarchive", "reply", "forward", "delete"},
    "sent": {"forward", "delete"},
    "draft": {"edit", "delete"},
}


def delete_mail(environ, mail_id, box_mails, incoming_mail=True):
    """
    incoming_mail: True implies inbox or archive
                   False implies sent or draft
    """

    if environ["REQUEST_METHOD"].upper() != "DELETE":
        kwargs = {"allowed": ("DELETE",)}
        return api_view_405(environ, **kwargs)

    # print(mail_id, box_mails,"aa")
    if mail_id not in box_mails:
        kwargs_passing = {}
        return api_view_403(environ, **kwargs_passing)
    if incoming_mail:
        UserInbox.objects.update({"deleted": True}, {"mail_id": mail_id})
    else:
        UserSent.objects.update({"deleted": True}, {"mail_id": mail_id})

    message = "Mail deleted"
    status_code = "200 OK"
    return success_api_response(message=message, status_code=status_code)


def delete_inbox_api_view(environ, **kwargs):
    mail_id = kwargs["mail_id"]
    box_mails = get_inbox(environ)
    box_mails = {mail.mail_id for mail in box_mails}
    return delete_mail(environ, mail_id, box_mails, incoming_mail=True)


def delete_archives_api_view(environ, **kwargs):
    mail_id = kwargs["mail_id"]
    box_mails = get_archives(environ)
    box_mails = {mail.mail_id for mail in box_mails}
    return delete_mail(environ, mail_id, box_mails, incoming_mail=True)


def delete_sent_mail_api_view(environ, **kwargs):
    mail_id = kwargs["mail_id"]
    box_mails = get_send_mails(environ)
    box_mails = {mail.id for mail in box_mails}
    return delete_mail(environ, mail_id, box_mails, incoming_mail=False)


def delete_draft_mails_api_view(environ, **kwargs):
    mail_id = kwargs["mail_id"]
    box_mails = get_draft_mails(environ)
    box_mails = {mail.id for mail in box_mails}
    return delete_mail(environ, mail_id, box_mails, incoming_mail=False)


def archive_unarchive_mail(environ, mail_id, box_mails, archive=True):
    # if archive is True it tries to archive mail if mail is in inbox
    # if archive is False it tries to unarchive mail if mail is in archives mail

    if environ["REQUEST_METHOD"].upper() != "PUT":
        kwargs = {"allowed": ("PUT",)}
        return api_view_405(environ, **kwargs)

    if mail_id not in box_mails:
        kwargs_passing = {}
        return api_view_403(environ, **kwargs_passing)

    # archive => True => Try to archive
    # archive => False => Try to unarchive

    UserInbox.objects.update({"archived_mail": archive}, {"mail_id": mail_id})

    message = "Mail archived" if archive else "Mail unarchived"
    status_code = "200 OK"
    return success_api_response(message=message, status_code=status_code)


def archive_mail_api_view(environ, **kwargs):
    mail_id = kwargs["mail_id"]
    box_mails = get_inbox(environ)
    box_mails = {mail.mail_id for mail in box_mails}
    return archive_unarchive_mail(environ, mail_id, box_mails, archive=True)


def unarchive_mail_api_view(environ, **kwargs):
    mail_id = kwargs["mail_id"]
    box_mails = box_mails = get_archives(environ)
    box_mails = {mail.mail_id for mail in box_mails}
    return archive_unarchive_mail(environ, mail_id, box_mails, archive=False)


def mail_interactions_view(environ, **kwargs):

    response_body = ""
    # redirect_data_response_headers = redirect_view('302 FOUND', '/inbox')

    # user_id = get_user_from_environ(environ)
    mail_id = kwargs["mail_id"]
    page = kwargs["page"]

    form_field_object = form_with_file_parsing(environ)

    user_interaction = form_field_object.getvalue("interaction")

    # Important, to get mail_id from the get functions, there are difference btw key name in the methods used
    # mail.mail_id in inbox and archive

    # mail.id in sent and draft
    if page == "inbox":
        box_mails = get_inbox(environ)
        box_mails = {mail.mail_id for mail in box_mails}
        redirect_data_response_headers = redirect_view("302 FOUND", "/inbox")

    elif page == "archive":
        box_mails = get_archives(environ)
        box_mails = {mail.mail_id for mail in box_mails}
        redirect_data_response_headers = redirect_view("302 FOUND", "/archives")

    # sent => past, sent mails
    elif page == "sent":
        box_mails = get_send_mails(environ)
        box_mails = {mail.id for mail in box_mails}
        redirect_data_response_headers = redirect_view("302 FOUND", "/sent-mails")

    elif page == "draft":
        box_mails = get_draft_mails(environ)
        box_mails = {mail.id for mail in box_mails}
        redirect_data_response_headers = redirect_view("302 FOUND", "/draft-mails")

    # print(user_interaction, page)
    if mail_id not in box_mails or user_interaction not in allowed_actions[page]:
        if mail_id not in box_mails:
            print("mail abscent")
        else:
            print(f"action {user_interaction}not allowed in the page {page}")
        kwargs_passing = {}
        print("Access denied")
        # Access denied
        return view_403(environ, **kwargs_passing)

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

    elif user_interaction == "edit" and page == "draft":
        url_to_redirect = f"/draft-mails/edit-draft/{mail_id}/"

        response_body = ""
        status = "302 FOUND"
        redirect_data_response_headers = redirect_view(status, url_to_redirect)
        return response_body, redirect_data_response_headers

    return response_body, redirect_data_response_headers
