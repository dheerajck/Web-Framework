from ...utils.session_handler import get_user_from_environ
from .draft_views import get_draft_mails, get_receivers_dict
from ...utils.template_handlers import render_template
from ..views1 import view_403

from ...utils.mail_utilites import draft_edit

from ...utils.mail_utilites import get_receivers_id_from_mail, get_attachment_link_from_name

from ...utils.post_form_handler import form_with_file_parsing
from ...utils.redirect_functions import redirect_to_dashboard_module


def edit_draft_mail_render_view(environ, **kwargs):
    # user_id = get_user_from_environ(environ)
    # start
    mail_id = kwargs["mail_id"]

    draft_mails = get_draft_mails(environ)

    draft_mails_dictionary = {mail.id: mail for mail in draft_mails}

    if mail_id not in draft_mails_dictionary:
        print("Permission denied")
        # kwargs is impotant
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

    # _________________________________________________________

    Attachment = mail_to_edit.attachment or ''
    Attachment_link = ''
    if Attachment:
        Attachment_link = get_attachment_link_from_name(Attachment) or ''
        # creating a label
        if Attachment_link:
            Attachment_link = f'<label for="attachment"> Uploaded file {Attachment_link}</label>'
    # _________________________________________________________
    print(mail_to_edit)

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
    }

    print(context)
    # context is not passing like kwarg, just using context = context for making it clear

    start_response_headers: dict = {}
    return render_template("edit-mail.html", context=context), start_response_headers


def edit_draft_mail_post_view(environ, **kwargs):

    print(form_field_storage := form_with_file_parsing(environ))
    print("########################################################1")
    sender_id = get_user_from_environ(environ)
    mail_id = kwargs["mail_id"]

    draft_mails = get_draft_mails(environ)

    draft_mails_dictionary = {mail.id: mail for mail in draft_mails}

    if mail_id not in draft_mails_dictionary:
        print("Permission denied")
        # kwargs is impotant
        kwargs_passing = {}
        return view_403(environ, **kwargs_passing)

    # sender_id = get_user_from_environ(environ)

    if environ['REQUEST_METHOD'].upper() != 'POST':
        return redirect_to_dashboard
        # pass  # dashboard

    form_field_storage = form_with_file_parsing(environ)

    receivers_mails: list = form_field_storage.getvalue('to_list').split(",")
    button = form_field_storage.getvalue('submit_input')

    if len(receivers_mails) == 0 and button == "sent":
        # if email doesnt exist redirect to form with error and button is send,
        # currently redirects to dashboard(no email is same as invalid email so the mail will not be send)
        # can add required in input field if draft was not an option
        pass

    # get_receivers_id_from_mail accepts a list of receiver mails and returns a list of "user id", "group id"and "invalid mail"
    group_list, user_list, invalid_email_list = get_receivers_id_from_mail(receivers_mails)

    if len(invalid_email_list) > 0:
        # invalid email id present
        pass

    print("xyx")
    print(button)
    if button in {"send", "draft"}:

        print(f'doing{button}')

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
