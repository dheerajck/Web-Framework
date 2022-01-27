from ..orm.models import User, Groups, UserGroup

from ..orm.models import Mails, UserSent, UserInbox

from ..utils.datetime_module import get_current_time_tz
import uuid


def get_mail_data_dict(form_field_object):
    # this should not return key error since this is name of a filed in the html form #
    #  this key will be always be present with a value or null string
    if "attachment" in form_field_object:
        fileitem = form_field_object["attachment"]
        # traversal file name
        file_name = fileitem.filename
    else:
        # traversal file name
        file_name = False

    # form_field_storage gives all fields except files on string format, files on binary format
    # draft is false by default, "draft" is True can be add form send_draft
    mail_data = {
        "created_date": get_current_time_tz(),
        "title": form_field_object.getvalue("title"),
        "body": form_field_object.getvalue("body"),
    }

    print("########################################################")
    print(mail_data)
    mail_data = {key: value for key, value in mail_data.items() if value != ""}
    print(mail_data)
    # print(22, form_field_object.getvalue('attachment'))
    if file_name:
        file_name = mail_data["attachment"]
        random_string = str(uuid.uuid4())
        new_file_name = f"{random_string}__{file_name}"
        mail_data["attachment"] = new_file_name

        # saving file
        print()
        directory = "webapp/media/"
        # file name contain extension, so no need to add it
        # saves files to media folder
        # serve this file as downloadable or viewable if browser supports
        file_path = directory + new_file_name
        print(file_path, "xxA")
        with open(file_path, mode="wb") as f:
            # print(form_field_object.getvalue('attachment'))
            f.write(form_field_object.getvalue("attachment"))

    return mail_data


# support for get_receivers_id_from_mail
def is_mail_group(mail):
    data = Groups.objects.select({"id"}, {"group_mail": mail})
    if len(data) == 0:
        return False
    else:
        return data[0].id


# support for get_receivers_id_from_mail
def is_mail_user(mail):
    data = User.objects.select({"id"}, {"email": mail})
    if len(data) == 0:
        return False
    else:
        return data[0].id


# mail sending util
def get_receivers_id_from_mail(receivers_list):
    # get_receivers_id_from_mail accepts a list of receiver mails and returns a list of "user id", "group id"and "invalid mail"

    group_list = []
    user_list = []
    invalid_email_list = []

    for mail in receivers_list:
        mail = mail.strip()

        group_id = is_mail_group(mail)
        if group_id:
            group_list.append(group_id)
            continue

        user_id = is_mail_user(mail)
        if user_id:
            user_list.append(user_id)
            continue
        # if not the mail doesnt exist
        invalid_email_list.append(mail)

    return group_list, user_list, invalid_email_list


def send_mail(sender_id, user_list, group_list, form_field_object, draft=False):
    # delete mail if its in draft
    mail_data_dict = get_mail_data_dict(form_field_object)

    if draft is True:
        mail_data_dict["draft"] = True

    # add to mail table
    mail_id = Mails.objects.create(new_data=mail_data_dict)
    print(mail_id)
    # added mail link to UserSent Model
    UserSent.objects.create(new_data={"user_id": sender_id, "mail_id": mail_id})

    list_of_datas_user = []

    for user_id in user_list:
        list_of_datas_user.append({"user_id": user_id, "mail_id": mail_id})

    if len(list_of_datas_user) != 0:
        """
        add users who received the mail
        """
        UserInbox.objects.bulk_insert(list_of_datas_user)

    memebers_list_from_all_groups = []
    # implemented to return empty list if field in A, if A is empty container
    if len(group_list) > 0:
        # get all members of each group present in the mail
        memebers_list_from_all_groups = UserGroup.objects.select(
            {"user_id", "group_id"},
            {"group_id": group_list},
            0,  # only one element in filter filed so AND or OR gives will both will have no effect here
            1,
        )

    list_of_datas_user_with_group_id = []
    for users in memebers_list_from_all_groups:
        list_of_datas_user_with_group_id.append(
            {"user_id": users.user_id, "group_id": users.group_id, "mail_id": mail_id}
        )

    if len(list_of_datas_user_with_group_id) != 0:
        """
        add users who received the mail
        """
        UserInbox.objects.bulk_insert(list_of_datas_user_with_group_id)

    # multiple insert orm create

    # multiple insert user foreign key

    # multiple insert group foreign key


def send_draft(sender_id, user_list, group_list, form_field_object):
    send_mail(sender_id, user_list, group_list, form_field_object, draft=True)


# _____________________________________


def draft_edit(
    mail_id,
    user_input_submit_value,
    sender_id,
    user_list,
    group_list,
    form_field_object,
):
    # delete and insert is the easier way to do here, doing that, CASCADE is present on foreign keys refering mail id

    Mails.objects.delete(id=mail_id)
    data_dict = get_mail_data_dict(form_field_object)

    if user_input_submit_value == "draft":
        data_dict["draft"] = True

    mail_id = Mails.objects.create(new_data=data_dict)
    print(mail_id)
    # added mail link to UserSent Model
    UserSent.objects.create(new_data={"user_id": sender_id, "mail_id": mail_id})

    list_of_datas_user = []

    for user_id in user_list:
        list_of_datas_user.append({"user_id": user_id, "mail_id": mail_id})
    print(list_of_datas_user, "xxak")
    if len(list_of_datas_user) != 0:
        """
        add users who received the mail
        """

        UserInbox.objects.bulk_insert(list_of_datas_user)

    memebers_list_from_all_groups = []
    # implemented to return empty list if field in A, if A is empty container
    if len(group_list) > 0:
        # get all members of each group present in the mail
        memebers_list_from_all_groups = UserGroup.objects.select(
            {"user_id", "group_id"},
            {"group_id": group_list},
            0,  # only one element in filter filed so AND or OR gives will both will have no effect here
            1,
        )

    list_of_datas_user_with_group_id = []
    for users in memebers_list_from_all_groups:
        list_of_datas_user_with_group_id.append(
            {"user_id": users.user_id, "group_id": users.group_id, "mail_id": mail_id}
        )

    if len(list_of_datas_user_with_group_id) != 0:
        """
        add users who received the mail
        """
        UserInbox.objects.bulk_insert(list_of_datas_user_with_group_id)

    #
    # if user_input_submit_value is "send":
    #     # does automatic by mail_data_dict["draft"] = True, wait it dont do it
    #     mail_data_dict["draft"] = False
    #     # sender is still the same, no change, its his draft


def get_attachment_link_from_name(attachment_name):
    link_html_tag = ""
    if attachment_name is not None:
        file_name = attachment_name.split("__")[-1]
        file_directory = "/media/"
        file_link = f"{file_directory}{attachment_name}"
        link_html_tag = f"<a download={file_name} href={file_link}>attachment link</a>"
    return link_html_tag


def is_mail_empty(form_object):

    # fileitem = form_object['attachment']
    fileitem = ""
    file_name = ""
    if "attachment" in form_object:
        fileitem = form_object["attachment"]
        if fileitem.filename is not None:
            file_name = fileitem.filename.strip()

    params = {}
    for key in form_object.keys():
        if key == "attachment":
            continue
        value = form_object[key].value
        params[key] = value

    # form field object doesnt have get method
    # title = form_object.getvalue('title').strip()
    # body = form_object.getvalue('body').strip()
    title = params.get("title", "").strip()
    body = params.get("body", "").strip()

    if {title, body, file_name} == {""}:
        return True
    return False


from ast import literal_eval
from ..orm.models import SessionDb
from .template_handlers import render_template


def data_from_session_save_load(data_from_db: list):

    data = data_from_db[0]
    session_id_to_delete = data.id

    data_string_save = data.data_serialized
    data_dict = literal_eval(data_string_save)

    # use get per doc of get_receivers_dict method
    receivers_of_this_mail = data_dict["receivers"]
    To = receivers_of_this_mail

    Title = data_dict["title"]
    # print(f"{Title=}")
    Body = data_dict["body"]
    Attachment = data_dict["attachment"]
    to_mail_warning = data_dict["to_mail_warning"]
    need_some_data_to_send_mail_warning = data_dict[
        "need_some_data_to_send_mail_warning"
    ]
    SessionDb.objects.delete(id=session_id_to_delete)

    Attachment_link = ""
    if Attachment:
        Attachment_link = get_attachment_link_from_name(Attachment) or ""
        # creating a label
        # Attachment_link = f'<label for="attachment"> Uploaded file {Attachment_link}</label>'
        if Attachment_link:
            Attachment_link = f'<label for="attachment">{Attachment_link}</label>'

    context = {
        # "from": From_Address,
        # "from_name": From_Name,
        #
        # "mail_id": mail_id,
        "To": To,
        "Title": Title,
        "Body": Body,
        "Attachment_link": Attachment_link,
        "link_to_redirect": "/compose-mail-post-view/",
        "to_mail_warning": to_mail_warning,
        "need_some_data_to_send_mail_warning": need_some_data_to_send_mail_warning,
    }

    start_response_headers: dict = {}

    return render_template("edit-mail.html", context=context), start_response_headers
