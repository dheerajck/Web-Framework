from ...utils.post_form_handler import form_with_file_parsing
from ...utils.session_handler import get_user_from_environ
from ...utils.template_handlers import render_template

from ..views1 import view_403
from ...utils.redirect_functions import redirect_view
from .inbox_view import get_inbox


from ...orm.models import Mails


def mail_interactiions_view(environ, **kwargs):

    response_body = ''
    redirect_data_response_headers = redirect_view('302 FOUND', '/inbox')

    print("///////////////////////////////////////////////")
    # user_id = get_user_from_environ(environ)
    mail_id = kwargs["mail_id"]
    form_field_object = form_with_file_parsing(environ)
    user_interaction = form_field_object.getvalue('interaction')
    print(user_interaction)

    inbox_mails = get_inbox(environ)
    inbox_mails = {mail.id for mail in inbox_mails}
    print(inbox_mails)
    print("///////////////////////////////////////////////////////////////////////")
    if mail_id not in inbox_mails:
        kwargs_passing = {}
        print("no")
        # Access denied
        return view_403(environ, **kwargs_passing)

    print("hi")

    if user_interaction == "archive":
        Mails.objects.update({"archives": True}, {"id": mail_id})
    elif user_interaction == "delete":
        Mails.objects.delete(id=mail_id)

    elif user_interaction == "reply":
        pass
    elif user_interaction == "forward":
        pass

    return response_body, redirect_data_response_headers
