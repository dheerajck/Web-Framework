from ...utils.template_handlers import render_template
from ...utils.redirect_functions import redirect_to_dashboard_module

from ...utils.post_form_handler import form_with_file_parsing, cgiFieldStorageToDict
from ...utils.mail_utilites import send_mail, send_draft

from ...utils.session_handler import get_user_from_environ

start_response_headers: dict = {}

from ...orm.models import User, Groups


def is_mail_group(mail):
    data = Groups.objects.select({'id'}, {'group_mail': mail})
    if len(data) == 0:
        return False
    else:
        return data[0].id


def is_mail_user(mail):
    data = User.objects.select({'id'}, {'email': mail})
    if len(data) == 0:
        return False
    else:
        return data[0].id


def get_receivers_id(receivers_list):

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
    if len(receivers_mails) == 0 and button == "sent":
        # if email doesnt exist redirect to form with error and button is send
        pass

    group_list, user_list, invalid_email_list = get_receivers_id(receivers_mails)

    if len(invalid_email_list) > 0:
        # invalid email id present
        pass

    if button == "sent":
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
