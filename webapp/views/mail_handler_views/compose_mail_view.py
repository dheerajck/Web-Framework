from ...utils.template_handlers import render_template
from ...utils.redirect_functions import redirect_to_dashboard_module

from ...utils.post_form_handler import form_with_file_parsing, cgiFieldStorageToDict
from ...utils.mail_utilites import send_mail, send_draft, get_receivers_id_from_mail

from ...utils.session_handler import get_user_from_environ


start_response_headers: dict = {}


def compose_mail_view(environ, **kwargs):
    return render_template("compose-mail-folder/compose-mail.html", context={}), start_response_headers


def compose_mail_post_view(environ, **kwargs):

    sender_id = get_user_from_environ(environ)
    print()
    print("START")
    if environ['REQUEST_METHOD'].upper() != 'POST':
        return redirect_to_dashboard
        # pass  # dashboard

    form_field_storage = form_with_file_parsing(environ)
    # print(form_field_storage.getvalue('attachment'))
    print("sas/da")

    # this wont throw error since form returns attachment with no datas
    fileitem = form_field_storage['attachment']

    button = form_field_storage.getvalue('submit_input')
    print(button)

    receivers_mails: list = form_field_storage.getvalue('to_list').split(",")
    # draft can have no senders email this is checked here  to bypass draft mails
    if len(receivers_mails) == 0 and button == "send":
        # if email doesnt exist redirect to form with error and button is send,
        # currently redirects to dashboard(no email is same as invalid email so the mail will not be send)
        # can add required in input field if draft was not an option
        pass

    # get_receivers_id_from_mail accepts a list of receiver mails and returns a list of "user id", "group id"and "invalid mail"
    group_list, user_list, invalid_email_list = get_receivers_id_from_mail(receivers_mails)

    if len(invalid_email_list) > 0:
        # invalid email id present
        pass

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
