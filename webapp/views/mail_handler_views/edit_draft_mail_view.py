from ...utils.session_handler import get_user_from_environ
from .draft_views import get_draft_mails, get_receivers_dict
from ...utils.template_handlers import render_template
from ..views1 import view_403

from ...utils.mail_utilites import draft_edit, is_mail_empty

from ...utils.mail_utilites import get_receivers_id_from_mail, get_attachment_link_from_name

from ...utils.post_form_handler import form_with_file_parsing
from ...utils.redirect_functions import redirect_view_with_response_body, redirect_to_dashboard_module

from ...orm.models import SessionDb
from ast import literal_eval


def edit_draft_mail_render_view(environ, **kwargs):
    # user_id = get_user_from_environ(environ)
    # start
    sender_id = get_user_from_environ(environ)
    mail_id = kwargs["mail_id"]
    data = SessionDb.objects.select([], {"user_id": sender_id, "mail_id": mail_id})
    if len(data) == 0:

        draft_mails = get_draft_mails(environ)

        draft_mails_dictionary = {mail.id: mail for mail in draft_mails}

        if mail_id not in draft_mails_dictionary:
            print("Permission denied")
            # kwargs is important
            kwargs_passing = {}
            return view_403(environ, **kwargs_passing)
        # stop Can make a function

        mail_to_edit = draft_mails_dictionary[mail_id]

        receivers_dict = get_receivers_dict(draft_mails)

        # use get per doc of get_receivers_dict method
        receivers_of_this_mail = receivers_dict.get(mail_id, [])

        """
        Used to replace None ffrom fields by empty string ''
        >>> None or ""
        ''
        
        '''>>> "a" or ""
        'a'
    
        """

        To = receivers = ", ".join(receivers_of_this_mail) or ''
        # important
        # 'Mails' object is not subscriptable mail_to_edit["title"] will give Type error because mail_to_edit => Mail object is not subscriptable

        Title = mail_to_edit.title or ''
        # print(f"{Title=}")
        Body = mail_to_edit.body or ''
        Attachment = mail_to_edit.attachment or ''
        print(mail_to_edit)
        to_mail_warning = ''
        need_some_data_to_send_mail_warning = ''

    # _________________________________________________________
    else:
        data = data[0]
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
        need_some_data_to_send_mail_warning = data_dict["need_some_data_to_send_mail_warning"]
        SessionDb.objects.delete(id=session_id_to_delete)

    # _________________________________________________________


    Attachment_link = ''
    if Attachment:
        Attachment_link = get_attachment_link_from_name(Attachment) or ''
        # creating a label
        if Attachment_link:
            Attachment_link = f'<label for="attachment"> Uploaded file {Attachment_link}</label>'
    # _________________________________________________________


    context = {
        "from": "",
        "from_name": "",
        #
        "mail_id": mail_id,
        "To": To,
        "Title": Title,
        "Body": Body,
        "Attachment_link": Attachment_link,
        "link_to_redirect": f"/draft/edit-draft-mail-post/{mail_id}/",
        "to_mail_warning": to_mail_warning,
        "need_some_data_to_send_mail_warning": need_some_data_to_send_mail_warning
    }

    print(context)
    # context is not passing like kwarg, just using context = context for making it clear

    start_response_headers: dict = {}
    return render_template("edit-mail.html", context=context), start_response_headers


def edit_draft_mail_post_view(environ, **kwargs):

    form_field_storage = form_with_file_parsing(environ)
    # print(form_field_storage)
    print("########################################################1")
    sender_id = get_user_from_environ(environ)
    mail_id = kwargs["mail_id"]

    draft_mails = get_draft_mails(environ)

    draft_mails_dictionary = {mail.id: mail for mail in draft_mails}

    if mail_id not in draft_mails_dictionary:
        print("Permission denied")
        # kwargs is important
        kwargs_passing = {}
        return view_403(environ, **kwargs_passing)

    # sender_id = get_user_from_environ(environ)

    if environ['REQUEST_METHOD'].upper() != 'POST':
        return redirect_to_dashboard_module()
        # pass  # dashboard

    form_field_storage = form_with_file_parsing(environ)
    empty_mail = False
    receivers_mails: list = form_field_storage.getvalue('to_list').split(",") # [''] if empty
    if receivers_mails == ['']: empty_mail = True


    button = form_field_storage.getvalue('submit_input')

    warning_dict = {"to_mail_warning": '', "need_some_data_to_send_mail_warning": ''}

    if button == "send":

        if empty_mail:
            warning_dict["to_mail_warning"] = "Enter a mail id"
            # if email doesnt exist redirect to form with error and button is send,
            # currently redirects to dashboard(no email is same as invalid email so the mail will not be send)
            # can add required in input field if draft was not an option
            pass
        if is_mail_empty(form_field_storage):
            warning_dict["need_some_data_to_send_mail_warning"] = 'Empty mail cant be send'

    # get_receivers_id_from_mail accepts a list of receiver mails and returns a list of "user id", "group id"and "invalid mail"
    group_list, user_list, invalid_email_list = get_receivers_id_from_mail(receivers_mails)

    # _____________________________________________________________________________________
    if len(invalid_email_list) > 0 and button == "send":
        invalid_mails = ", ".join(invalid_email_list)
        if warning_dict["to_mail_warning"] == '':
            # if not already set
            if len(invalid_email_list) == 1:
                warning_dict["to_mail_warning"] = f'{invalid_mails} is an invalid mail'
            else:
                warning_dict["to_mail_warning"] = f'{invalid_mails} are invalid mails'
        # invalid email id present
        pass
    if set(warning_dict.values()) != {''}:
        # warnings are present so dont send the mail
        from ...utils.post_form_handler import cgiFieldStorageToDict
        form_data_dict = cgiFieldStorageToDict(form_field_storage)
        form_data_dict.update(warning_dict)

        #removing invalid mails
        # receivers mail is list
        print(receivers_mails, invalid_email_list)
        for invalid in invalid_email_list:
            receivers_mails.remove(invalid)
        receiver_list = receivers_mails

        print(receivers_mails,11)
        receivers = ", ".join(receiver_list)
        receivers = receivers.strip()
        form_data_dict["receivers"] = receivers
        form_data_dict["save_type"] = "draft"
        serialized_data_string = str(form_data_dict)
        SessionDb.objects.create(new_data={"user_id": sender_id, "mail_id": mail_id, "data_serialized": serialized_data_string})

        status = '302 FOUND'
        url_to_redirect = f'/draft-mails/edit-draft/{mail_id}/'
        data_to_return = redirect_view_with_response_body(status, url_to_redirect)
        return data_to_return

    # _____________________________________________________________________________________



    print("xyx")
    print(button)
    if button in {"send", "draft"}:

        print(f'doing{button}')
        # draft_edit sends the mail or save it in draft depending on the button
        draft_edit(
            mail_id,
            button,
            sender_id,
            user_list,
            group_list,
            form_field_storage,
        )

        return redirect_to_dashboard_module()

    else:
        return redirect_to_dashboard_module()
