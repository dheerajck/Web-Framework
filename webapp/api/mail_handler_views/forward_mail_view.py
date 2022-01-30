from .inbox_view import get_inbox
from .archived_mail_view import get_archives
from .sent_mail_view import get_send_mails
from ...utils.mail_utilites import get_attachment_link_from_name

from ...utils.post_form_handler import form_with_file_parsing
from ...utils.mail_utilites import get_receivers_id_from_mail


# from ...utils.session_handler import get_user_from_environ
from ...utils.session_handler import get_user_details_from_environ

from ..views1 import success_api_response, error_api_response_codes
from ..views1 import api_view_403, api_view_405


from ...utils.session_handler import get_user_from_environ


from ...orm.models import UserGroup

from ...orm.models import Mails, UserSent, UserInbox

from ...utils.datetime_module import get_current_time_tz


import uuid


def get_mail_data_dict_from_dict(datas_from_db):

    # this should not return key error since this is name of a filed in the html form #
    #  this key will be always be present with a value or null string
    if "attachment" in datas_from_db:
        fileitem = datas_from_db["attachment"]
        # traversal file name
        file_name = fileitem.filename
    else:
        file_name = False

    # form_field_storage gives all fields except files on string format, files on binary format
    # draft is false by default, "draft" is True can be add form send_draft
    mail_data = {
        "created_date": get_current_time_tz(),
        "title": datas_from_db.get("title"),
        "body": datas_from_db.get("body"),
    }

    mail_data = {key: value for key, value in mail_data.items() if value != ""}

    # print(22, form_field_object.getvalue('attachment'))
    if file_name:
        file_name = mail_data["attachment"]
        random_string = str(uuid.uuid4())
        new_file_name = f"{random_string}__{file_name}"
        mail_data["attachment"] = new_file_name

        directory = "webapp/media/"
        file_path = directory + new_file_name
        print(file_path, "xxA")
        with open(file_path, mode="wb") as f:
            f.write(datas_from_db.getvalue("attachment"))
    return mail_data


def send_mail_draft_with_validation_fields(
    button, sender_id, receivers_mails, subject_of_mail, body_of_mail, attachment=None
):
    empty_mail = False
    receivers_mails: list = receivers_mails.split(",")  # [''] if empty
    if receivers_mails == [""]:
        empty_mail = True

    warning_dict = {"to_mail_warning": "", "need_some_data_to_send_mail_warning": ""}

    # draft can have no senders email this is checked here  to bypass draft mails

    no_client_errors_flag = True
    if button == "send":

        if empty_mail:
            warning_dict["to_mail_warning"] = "Enter a mail id"
            status_code = "422 Unprocessable Entity"
            no_client_errors_flag = False

        """
        if is_mail_empty(form_field_storage):
            status_code = "422 Unprocessable Entity"
            message = "There should be some data to send a mail"
            no_client_errors_flag = False
        """

        if subject_of_mail.strip() == "" and body_of_mail.strip() == "":
            status_code = "422 Unprocessable Entity"
            message = "There should be some data to send a mail"
            no_client_errors_flag = False

    group_list, user_list, invalid_email_list = get_receivers_id_from_mail(
        receivers_mails
    )

    if len(invalid_email_list) > 0 and button == "send":
        status_code = "422 Unprocessable Entity"
        message = {
            "error_reason": "Receivers list contains invalid mails",
            "invalid_mails": invalid_email_list,
        }
        no_client_errors_flag = False

    data_forwarding = get_mail_data_dict_from_dict(
        {"title": subject_of_mail, "body": body_of_mail}
    )
    if button == "send" and no_client_errors_flag:
        # {"attachment": "", "title": "", "body": ""}
        # {"title": "", "body": ""}
        # receivers_mails, Subject_to_print, Body
        data_forwarding = get_mail_data_dict_from_dict(
            {"title": subject_of_mail, "body": body_of_mail}
        )
        send_mail_with_data_dict(
            sender_id,
            user_list,
            group_list,
            data_forwarding,
        )

        if data_forwarding["title"].startswith("Fwd:"):
            message = "Forwarded the mail successfully"
        elif data_forwarding["title"].startswith("Re:"):
            message = "Replied to the mail successfully"
        else:
            message = "Mail send successfully"
        return success_api_response(message)

    elif button == "draft" and no_client_errors_flag:

        send_draft_with_data_dict(
            sender_id,
            user_list,
            group_list,
            data_forwarding,
        )

        message = "Draft saved"
        return success_api_response(message)
    elif no_client_errors_flag:
        # no other error code till now so its bad request
        status_code = "400 Bad Request"
        message = "The server could not understand the request due to invalid syntax."
    return error_api_response_codes(status_code, message)


def send_mail_with_data_dict(sender_id, user_list, group_list, data_dict, draft=False):
    # delete mail if its in draft
    data_forwarding = data_dict

    if draft is True:
        data_forwarding["draft"] = True
    # add to mail table
    mail_id = Mails.objects.create(new_data=data_forwarding)

    # added mail link to UserSent Model
    UserSent.objects.create(new_data={"user_id": sender_id, "mail_id": mail_id})

    list_of_datas_user = []

    for user_id in user_list:
        list_of_datas_user.append({"user_id": user_id, "mail_id": mail_id})

    if len(list_of_datas_user) != 0:
        UserInbox.objects.bulk_insert(list_of_datas_user)

    members_list_from_all_groups = []

    if len(group_list) > 0:
        # get all members of each group present in the mail
        members_list_from_all_groups = UserGroup.objects.select(
            {"user_id", "group_id"},
            {"group_id": group_list},
            0,
            1,
        )

    list_of_datas_user_with_group_id = []
    for users in members_list_from_all_groups:
        list_of_datas_user_with_group_id.append(
            {"user_id": users.user_id, "group_id": users.group_id, "mail_id": mail_id}
        )

    if len(list_of_datas_user_with_group_id) != 0:
        UserInbox.objects.bulk_insert(list_of_datas_user_with_group_id)


def send_draft_with_data_dict(sender_id, user_list, group_list, data_dict):
    send_mail_with_data_dict(sender_id, user_list, group_list, data_dict, draft=True)


def forward_mail_api_view(environ, **kwargs):
    """
    mail_id: mail id to forward should be included in the url
    """

    sender_id = get_user_from_environ(environ)
    mail_id = kwargs["mail_id"]
    forward_from = kwargs["box"]

    if environ["REQUEST_METHOD"].upper() != "GET":
        kwargs = {"allowed": ("GET",)}
        return api_view_405(environ, **kwargs)

    box_id_list = []
    if forward_from == "inbox":
        box_id_list = get_inbox(environ)
        box_id_dict = {mail.mail_id: mail for mail in box_id_list}

    elif forward_from == "archives":
        box_id_list = get_archives(environ)
        box_id_dict = {mail.mail_id: mail for mail in box_id_list}

    elif forward_from == "sent-mails":
        From_Address, From_Name = get_user_details_from_environ(
            environ, ["email", "name"]
        )

        box_id_list = get_send_mails(environ)
        box_id_dict = {mail.id: mail for mail in box_id_list}

        To_Address = box_id_dict[mail_id].user_mail
    # __________________________________________________________________________________________

    if mail_id not in box_id_dict:
        # Access denied
        kwagrs = {}
        return api_view_403(environ, **kwagrs)

    forwarding_mails_object = box_id_dict[mail_id]
    form_field_storage = form_with_file_parsing(environ)

    # to_list = form_field_storage.getvalue("to_list")
    # button = form_field_storage.getvalue("mail_draft")
    to_list = ""

    if forward_from in ["inbox", "archives"]:
        # forward details of sent-mails configured above
        From_Address, From_Name = (
            forwarding_mails_object.email,
            forwarding_mails_object.name,
        )

        # get_user_details_from_environ returns a list containing needed field value, empty list if no match
        To_Address = get_user_details_from_environ(environ, ["email"])[
            0
        ]  # access 0th element

    Created_date = forwarding_mails_object.created_date
    Subject = forwarding_mails_object.title
    Body = forwarding_mails_object.body
    Attachment = forwarding_mails_object.attachment or ""
    # _______________________________________________________________________________________________

    Attachment_link = ""
    if Attachment:
        Attachment_link = get_attachment_link_from_name(Attachment) or ""
        # creating a label
        # Attachment_link = f'<label for="attachment"> Uploaded file {Attachment_link}</label>'
        if Attachment_link:
            Attachment_link = f'<label for="attachment">{Attachment_link}</label>'
    # __________________________________________________________________________________________

    Subject_to_print = f"Fwd: {Subject}"
    print(Subject_to_print, "Xass")
    print(From_Address, To_Address, "XXXXX")
    forwarding_mail_body = f"""


---------- Forwarded message ----------
From: {From_Name}
{From_Address}
Date: {Created_date}
Subject: {Subject}
To: {To_Address}


{Body}

Attachment link: {Attachment_link}
_______________________________________
"""
    data_to_forward_with_subject = {
        "Title": Subject_to_print,
        "Body": forwarding_mail_body,
    }
    return success_api_response(data_to_forward_with_subject)


def reply_mail_api_view(environ, **kwargs):
    """
    mail_id: mail id to forward should be included in the url
    """

    sender_id = get_user_from_environ(environ)
    mail_id = kwargs["mail_id"]

    forward_from = kwargs["box"]
    # for reply

    if environ["REQUEST_METHOD"].upper() != "GET":
        kwargs = {"allowed": ("GET",)}
        return api_view_405(environ, **kwargs)

    box_id_list = []
    if forward_from == "inbox":
        box_id_list = get_inbox(environ)
        box_id_dict = {mail.mail_id: mail for mail in box_id_list}

    elif forward_from == "archives":
        box_id_list = get_archives(environ)
        box_id_dict = {mail.mail_id: mail for mail in box_id_list}

    if mail_id not in box_id_dict:
        # Access denied
        kwagrs = {}
        return api_view_403(environ, **kwagrs)

    # here object of the mail to which reply data should be
    # created is replying_mails_object
    replying_mails_object = box_id_dict[mail_id]
    form_field_storage = form_with_file_parsing(environ)

    if forward_from in ["inbox", "archives"]:
        # forward details of sent-mails configured above
        From_Address, From_Name = (
            replying_mails_object.email,
            replying_mails_object.name,
        )

        # get_user_details_from_environ returns a list containing needed field value, empty list if no match
        To_Address = get_user_details_from_environ(environ, ["email"])[
            0
        ]  # access 0th element

    Created_date = replying_mails_object.created_date
    Subject = replying_mails_object.title
    Body = replying_mails_object.body
    Attachment = replying_mails_object.attachment or ""
    # _______________________________________________________________________________________________

    Attachment_link = ""
    if Attachment:
        Attachment_link = get_attachment_link_from_name(Attachment) or ""
        # creating a label
        # Attachment_link = f'<label for="attachment"> Uploaded file {Attachment_link}</label>'
        if Attachment_link:
            Attachment_link = f'<label for="attachment">{Attachment_link}</label>'
    # __________________________________________________________________________________________

    Subject_to_print = f"Re: {Subject}"
    replied_mail_body = f"""

---------- Replying to ----------
On {Created_date}, {From_Name}, {From_Address} wrote:

    {Body}

    Attachment link: {Attachment_link}
_______________________________________
"""
    data_to_reply_with_subject = {
        "To": From_Address,
        "Title": Subject_to_print,
        "Body": replied_mail_body,
    }
    return success_api_response(data_to_reply_with_subject)


def forward_mail_api_view_post(environ, **kwargs):
    """
    to_list: mails separated by comma
    """

    sender_id = get_user_from_environ(environ)
    mail_id = kwargs["mail_id"]
    forward_from = kwargs["box"]

    if environ["REQUEST_METHOD"].upper() != "POST":
        kwargs = {"allowed": ("POST",)}
        return api_view_405(environ, **kwargs)

    box_id_list = []
    if forward_from == "inbox":
        box_id_list = get_inbox(environ)
        box_id_dict = {mail.mail_id: mail for mail in box_id_list}

    elif forward_from == "archives":
        box_id_list = get_archives(environ)
        box_id_dict = {mail.mail_id: mail for mail in box_id_list}

    elif forward_from == "sent-mails":
        From_Address, From_Name = get_user_details_from_environ(
            environ, ["email", "name"]
        )

        box_id_list = get_send_mails(environ)
        box_id_dict = {mail.id: mail for mail in box_id_list}

        To_Address = box_id_dict[mail_id].user_mail
    # __________________________________________________________________________________________

    if mail_id not in box_id_dict:
        # Access denied
        kwagrs = {}
        return api_view_403(environ, **kwagrs)

    forwarding_mails_object = box_id_dict[mail_id]
    form_field_storage = form_with_file_parsing(environ)

    to_list = form_field_storage.getvalue("to_list")
    button = form_field_storage.getvalue("mail_draft")

    if forward_from in ["inbox", "archives"]:
        # forward details of sent-mails configured above
        From_Address, From_Name = (
            forwarding_mails_object.email,
            forwarding_mails_object.name,
        )

        # get_user_details_from_environ returns a list containing needed field value, empty list if no match
        To_Address = get_user_details_from_environ(environ, ["email"])[
            0
        ]  # access 0th element

    Created_date = forwarding_mails_object.created_date
    Subject = forwarding_mails_object.title
    Body = forwarding_mails_object.body
    Attachment = forwarding_mails_object.attachment or ""
    # _______________________________________________________________________________________________

    Attachment_link = ""
    if Attachment:
        Attachment_link = get_attachment_link_from_name(Attachment) or ""
        # creating a label
        # Attachment_link = f'<label for="attachment"> Uploaded file {Attachment_link}</label>'
        if Attachment_link:
            Attachment_link = f'<label for="attachment">{Attachment_link}</label>'
    # __________________________________________________________________________________________

    Subject_to_print = f"Fwd: {Subject}"
    print(Subject_to_print, "Xass")
    print(From_Address, To_Address, "XXXXX")
    Body = f"""


---------- Forwarded message ----------
From: {From_Name}
{From_Address}
Date: {Created_date}
Subject: {Subject}
To: {To_Address}


{Body}

Attachment link: {Attachment_link}
_______________________________________
"""

    return send_mail_draft_with_validation_fields(
        button, sender_id, to_list, Subject_to_print, Body
    )


def reply_mail_api_view_post(environ, **kwargs):
    """
    to_list: mails separated by comma
    body: body
    """

    sender_id = get_user_from_environ(environ)
    mail_id = kwargs["mail_id"]

    forward_from = kwargs["box"]
    # for reply

    if environ["REQUEST_METHOD"].upper() != "POST":
        kwargs = {"allowed": ("POST",)}
        return api_view_405(environ, **kwargs)

    box_id_list = []
    if forward_from == "inbox":
        box_id_list = get_inbox(environ)
        box_id_dict = {mail.mail_id: mail for mail in box_id_list}

    elif forward_from == "archives":
        box_id_list = get_archives(environ)
        box_id_dict = {mail.mail_id: mail for mail in box_id_list}

    if mail_id not in box_id_dict:
        # Access denied
        kwagrs = {}
        return api_view_403(environ, **kwagrs)

    replying_mails_object = box_id_dict[mail_id]
    form_field_storage = form_with_file_parsing(environ)

    body = form_field_storage.getvalue("body")
    button = form_field_storage.getvalue("mail_draft")

    if forward_from in ["inbox", "archives"]:
        # forward details of sent-mails configured above
        From_Address, From_Name = (
            replying_mails_object.email,
            replying_mails_object.name,
        )

        # get_user_details_from_environ returns a list containing needed field value, empty list if no match
        To_Address = get_user_details_from_environ(environ, ["email"])[
            0
        ]  # access 0th element

    Created_date = replying_mails_object.created_date
    Subject = replying_mails_object.title
    Body = replying_mails_object.body
    Attachment = replying_mails_object.attachment or ""
    # _______________________________________________________________________________________________

    Attachment_link = ""
    if Attachment:
        Attachment_link = get_attachment_link_from_name(Attachment) or ""
        # creating a label
        # Attachment_link = f'<label for="attachment"> Uploaded file {Attachment_link}</label>'
        if Attachment_link:
            Attachment_link = f'<label for="attachment">{Attachment_link}</label>'
    # __________________________________________________________________________________________

    Subject_to_print = f"Re: {Subject}"
    replied_mail_body = f"""

---------- Replying to ----------
On {Created_date}, {From_Name}, {From_Address} wrote:

    {Body}

    Attachment link: {Attachment_link}
_______________________________________
"""

    body = body + replied_mail_body

    return send_mail_draft_with_validation_fields(
        button, sender_id, From_Address, Subject_to_print, body
    )
