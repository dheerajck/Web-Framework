from ...utils.template_handlers import render_template
from ...utils.redirect_functions import redirect_to_dashboard_module

from ...utils.post_form_handler import form_with_file_parsing
from ...utils.mail_utilites import send_mail, send_draft, get_receivers_id_from_mail
from ...utils.session_handler import get_user_from_environ


from ...utils.mail_utilites import data_from_session_save_load, is_mail_empty
from ...utils.redirect_functions import redirect_view_with_response_body
from ...utils.post_form_handler import cgiFieldStorageToDict

from ...orm.models import SessionDb


start_response_headers: dict = {}


# def compose_mail_view(environ, **kwargs):
#     return render_template("compose-mail-folder/compose-mail.html", context={}), start_response_headers

# def compose_mail_post_view(environ, **kwargs):
#     if len(receivers_mails) == 0 and button == "send":
#         # if email doesnt exist redirect to form with error and button is send,
#         # currently redirects to dashboard(no email is same as invalid email so the mail will not be send)
#         # can add required in input field if draft was not an option
#         pass


def compose_mail_view(environ, **kwargs):
    sender_id = get_user_from_environ(environ)
    data_from_db = SessionDb.objects.select([], {"user_id": sender_id})
    if len(data_from_db) != 0:
        return data_from_session_save_load(data_from_db)
    return render_template("compose-mail-folder/compose-mail.html", context={}), start_response_headers


def compose_mail_post_view(environ, **kwargs):

    sender_id = get_user_from_environ(environ)
    print()
    print("START")

    if environ['REQUEST_METHOD'].upper() != 'POST':
        return redirect_to_dashboard_module()
        # pass  # dashboard

    form_field_storage = form_with_file_parsing(environ)

    # this wont throw error since form returns attachment with no datas
    # fileitem = form_field_storage['attachment']

    button = form_field_storage.getvalue('submit_input')
    print(button)

    receivers_mails: list = form_field_storage.getvalue('to_list').split(",")
    empty_mail = False

    receivers_mails: list = form_field_storage.getvalue('to_list').split(",")  # [''] if empty
    if receivers_mails == ['']:
        empty_mail = True

    warning_dict = {"to_mail_warning": '', "need_some_data_to_send_mail_warning": ''}

    # draft can have no senders email this is checked here  to bypass draft mails

    if button == "send":

        if empty_mail:
            warning_dict["to_mail_warning"] = "Enter a mail id"
            # if email doesnt exist redirect to form with error and button is send,
            # currently redirects to dashboard(no email is same as invalid email so the mail will not be send)
            # can add required in input field if draft was not an option

        if is_mail_empty(form_field_storage):
            warning_dict["need_some_data_to_send_mail_warning"] = 'Empty mail cant be send'

    # get_receivers_id_from_mail accepts a list of receiver mails and returns a list of "user id", "group id"and "invalid mail"
    group_list, user_list, invalid_email_list = get_receivers_id_from_mail(receivers_mails)

    if len(invalid_email_list) > 0 and button == "send":
        invalid_mails = ", ".join(invalid_email_list)
        if warning_dict["to_mail_warning"] == '':
            # if not already set
            if len(invalid_email_list) == 1:
                warning_dict["to_mail_warning"] = f'{invalid_mails} is an invalid mail'
            else:
                warning_dict["to_mail_warning"] = f'{invalid_mails} are invalid mails'

    if set(warning_dict.values()) != {''}:
        # warnings are present so dont send the mail

        form_data_dict = cgiFieldStorageToDict(form_field_storage)
        form_data_dict.update(warning_dict)

        # removing invalid mails
        # receivers mail is list
        print(receivers_mails, invalid_email_list)
        for invalid in invalid_email_list:
            receivers_mails.remove(invalid)
        receiver_list = receivers_mails

        receivers = ", ".join(receiver_list)
        receivers = receivers.strip()
        form_data_dict["receivers"] = receivers
        form_data_dict["save_type"] = "inbox"
        serialized_data_string = str(form_data_dict)
        SessionDb.objects.create(new_data={"user_id": sender_id, "data_serialized": serialized_data_string})

        status = '302 FOUND'
        url_to_redirect = f'/dashboard/compose-mail/'
        data_to_return = redirect_view_with_response_body(status, url_to_redirect)
        return data_to_return

    if button == "send":
        print('send')

        send_mail(
            sender_id,
            user_list,
            group_list,
            form_field_storage,
        )

        return redirect_to_dashboard_module()

    elif button == "draft":

        print('draft')
        send_draft(
            sender_id,
            user_list,
            group_list,
            form_field_storage,
        )

        return redirect_to_dashboard_module()
    else:
        return redirect_to_dashboard_module()
