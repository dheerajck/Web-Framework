from .inbox_view import get_inbox
from .archived_mail_view import get_archives
from .sent_mail_view import get_send_mails
from ...utils.template_handlers import render_template

# from ...utils.session_handler import get_user_from_environ
from ...utils.session_handler import get_user_details_from_environ
from ..views1 import view_403


def check_user_permission(mail_id, box_id):
    if mail_id not in box_mails or user_interaction not in allowed_actions[page]:
        kwargs_passing = {}
        print("no")
        # Access denied
        return view_403(environ, **kwargs_passing)


def forward_mail_render_view(environ, **kwagrs):
    # user_id = get_user_from_environ(environ)
    user_id = get_user_details_from_environ(environ, ["id"])
    mail_id = kwagrs["mail_id"]
    forward_from = kwagrs["forward_from"]

    box_id_list = []
    if forward_from == "inbox":
        box_id_list = get_inbox(environ)
        box_id_dict = {mail.mail_id: mail for mail in box_id_list}

    elif forward_from == "archives":
        box_id_list = get_archives(environ)
        box_id_dict = {mail.mail_id: mail for mail in box_id_list}

    elif forward_from == "sent-mails":
        From_Address, From_Name = get_user_details_from_environ(environ, ["email", "name"])

        box_id_list = get_send_mails(environ)
        box_id_dict = {mail.id: mail for mail in box_id_list}

        To_Address = box_id_dict[mail_id].user_mail
    # __________________________________________________________________________________________

    # if the forwarded from location is not in these three, which is double checked
    # from url handler and here or if mail id not in the forward requesint box mail's
    # permission is denied
    print(box_id_dict.keys(), "xp")
    # if mail_id not in box_id_list:
    if mail_id not in box_id_dict:
        # Access denied
        kwagrs = {}
        return view_403(environ, **kwagrs)

    forwarding_mails_object = box_id_dict[mail_id]

    if forward_from in ["inbox", "archives"]:
        From_Address, From_Name = forwarding_mails_object.email, forwarding_mails_object.name

        # get_user_details_from_environ returns a list containing needed field value, empty list if no match
        To_Address = get_user_details_from_environ(environ, ["email"])[0]  # access 0th element

    Created_date = forwarding_mails_object.created_date
    Subject = forwarding_mails_object.title
    Body = forwarding_mails_object.body
    Attachment = forwarding_mails_object.attachment or ''
    Attachment_link = ''
    if Attachment:
        Attachment_link = get_attachment_link_from_name(Attachment) or ''
        # creating a label
        if Attachment_link:
            Attachment_link = f'<label for="attachment"> Uploaded file {Attachment_link}</label>'
    # __________________________________________________________________________________________

    Subject_to_print = f"Fwd: {Subject}"
    print(Subject_to_print, "Xass")

    Body = f"""

    ---------- Forwarded message ----------
    From: {From_Name} 
    <{From_Address}>
    Date: {Created_date}
    Subject: {Subject}
    To: <{To_Address}>
    
    
    {Body}

    """

    context = {
        "from": From_Address,
        "from_name": From_Name,
        #
        "mail_id": mail_id,
        "To": '',
        "Title": Subject_to_print,
        "Body": Body,
        "Attachment_link": Attachment_link,
        "link_to_redirect": "/compose-mail-post-view/",
    }

    start_response_headers: dict = {}

    return render_template("edit-mail.html", context=context), start_response_headers
