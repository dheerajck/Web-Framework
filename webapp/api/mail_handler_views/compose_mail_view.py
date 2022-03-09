from ...utils.post_form_handler import form_with_file_parsing
from ...utils.mail_utilites import send_mail, send_draft, get_receivers_id_from_mail
from ...utils.session_handler import get_user_from_environ
from ...utils.mail_utilites import is_mail_empty
from webapp.api.views1 import api_view_405

import json


start_response_headers: dict = {}


def error_api_response_codes(status, message):
    status = status
    response_headers = [
        ('Content-type', 'application/json'),
    ]

    response_body = {'message': message, 'status': status}
    response_body = json.dumps(response_body, indent=4)

    response_headers.append(('Content-length', str(len(response_body))))
    start_response_headers: dict = {'status': status, 'response_headers': response_headers}
    return response_body, start_response_headers


def success_api_response(message):
    status = "200 OK"
    response_headers = [
        ('Content-type', 'application/json'),
    ]

    response_body = {'message': message, 'status': status}
    response_body = json.dumps(response_body)

    response_headers.append(('Content-length', str(len(response_body))))
    start_response_headers: dict = {'status': status, 'response_headers': response_headers}
    return response_body, start_response_headers


def compose_mail_api_view(environ, **kwargs):

    '''
    to_list: emails separated by comma
    title: mail title should be specified
    body: mail body should be specified
    attachment: attachments if any
    mail_draft: send to send mail, draft to save it as a draft

    '''

    sender_id = get_user_from_environ(environ)
    print()
    print("START")

    if environ['REQUEST_METHOD'].upper() != 'POST':
        kwargs = {"allowed": ("POST",)}
        return api_view_405(environ, **kwargs)

    form_field_storage = form_with_file_parsing(environ)

    button = form_field_storage.getvalue('mail_draft')

    receivers_mails: list = form_field_storage.getvalue('to_list').split(",")
    empty_mail = False

    receivers_mails: list = form_field_storage.getvalue('to_list').split(",")  # [''] if empty
    if receivers_mails == ['']:
        empty_mail = True

    warning_dict = {"to_mail_warning": '', "need_some_data_to_send_mail_warning": ''}

    # draft can have no senders email this is checked here  to bypass draft mails

    no_client_errors_flag = True
    if button == "send":

        if empty_mail:
            warning_dict["to_mail_warning"] = "Enter a mail id"
            status_code = "422 Unprocessable Entity"
            no_client_errors_flag = False

        if is_mail_empty(form_field_storage):
            status_code = "422 Unprocessable Entity"
            message = "There should be some data to send a mail"
            no_client_errors_flag = False

    group_list, user_list, invalid_email_list = get_receivers_id_from_mail(receivers_mails)

    if len(invalid_email_list) > 0 and button == "send":
        status_code = "422 Unprocessable Entity"
        message = {"error_reason": "Receivers list contains invalid mails", "invalid_mails": invalid_email_list}
        no_client_errors_flag = False

    if button == "send" and no_client_errors_flag:

        send_mail(
            sender_id,
            user_list,
            group_list,
            form_field_storage,
        )
        message = 'Mail send successfully'
        return success_api_response(message)

    elif button == "draft" and no_client_errors_flag:

        send_draft(
            sender_id,
            user_list,
            group_list,
            form_field_storage,
        )

        message = 'Draft saved'
        return success_api_response(message)
    elif no_client_errors_flag:
        # no other error code till now so it should be handled as bad request
        status_code = "400 Bad Request"
        message = "The server could not understand the request due to invalid syntax."
    return error_api_response_codes(status_code, message)
