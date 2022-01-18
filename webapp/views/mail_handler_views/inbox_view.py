from ...utils.template_handlers import render_template

from ...utils.session_handler import get_user_from_environ
from ...orm.models import User, UserGroup
from ...orm.models import Mails, MailReceivers


def view_inbox(environ, **kwargs):
    '''
    select is not loop, so row containing values which satisifes condition are retrieved
    rows are not multiplied here, every row with mail_id in LIST which are Archived are retrievd,
    important => data retireved never greater than data in the table
    if a user sends same mail through user, groups
    only one copy will reach here since mail id is unique which is actually good
    '''

    receivers_list = []
    user_id = get_user_from_environ(environ)
    users_groups = UserGroup.objects.select({"group_id"}, {'user_id': user_id})
    print(users_groups)
    users_groups_id = [user.group_id for user in users_groups]

    users_groups_id = tuple(users_groups_id)
    print(user_id, users_groups_id)
    print("^^^^^^^^^^^^^^^^^^^^^^^^")

    print("INBOX USER")

    filter_conditions = {"receiver_user": user_id, "receiver_group": users_groups_id}
    # better make user id a tuple, and avoid type(value) == int condition
    # Receiver of a mail should satisfy one of this two condition => OR
    filter_conditions = {
        key: value for key, value in filter_conditions.items() if type(value) == int or len(value) != 0
    }
    print(filter_conditions)
    print("user id", user_id)
    # 1 => OR 1 => IN
    mails_id_objects = MailReceivers.objects.select(
        {"mail_id"},
        filter_conditions,
        1,  # 1 => OR
        1,  # 1 => field IN tuples , 0 => field=value
    )
    mails_id_list = [mail_object.mail_id for mail_object in mails_id_objects]
    print(mails_id_list, "FOUND")

    mails_id_tuple = tuple(mails_id_list)
    print(mails_id_tuple, "FOUND")

    filter_condition = {"id": mails_id_tuple, "archives": False}

    if len(mails_id_tuple) == 0:
        # found when creating draftbox
        print("no mails")
        inbox = []

    else:
        inbox = Mails.objects.select(
            {},
            filter_condition,
            0,  # 0 => AND
            1,  # 1 => field IN tuples , 0 => field=value
            ("created_date",),  # order by created_date descending order
        )
    print(inbox)

    mail_div = ''
    for each_mail in inbox:
        print(each_mail)

        link_html_tag = ''
        if each_mail.attachment is not None:

            file_name = each_mail.attachment.split("__")[-1]
            file_directory = '/media/'
            file_link = f"{file_directory}{each_mail.attachment}"
            link_html_tag = f"<a download={file_name} href={file_link}>attachment link</a>"
        #  space present in comment tag after --  will make the template not render
        # <!-- add datetime sort Done -- >
        mail_div += f'''
        
        <div>
         <!-- add datetime sort Done -->
      
        
        <h3>{each_mail.created_date}</h3>
        <h2>{each_mail.title}</h2>
        <p>from:{User.objects.select_one(["email"], {"id":each_mail.sender})}</p>
        <pre>{each_mail.body}</pre>
        {link_html_tag}
        <form action="inbox-actions/" method="post">
            <input type="button" name="interaction" value="archive" placeholder="archive">
            <input type="button" name="interaction" value="reply" placeholder="reply">
            <input type="button" name="interaction" value="forward" placeholder="forward">
            <input type="button" name="interaction" value="delete" placeholder="delete">
        </form>
        <hr>
        </div>'''

    # if for loop is not executed because there are no mails in inbox of user
    if mail_div == "":
        mail_div = "<h1>No mails in Inbox</h1>"

    context = {'title_of_page': "inbox", "mails": mail_div}
    response_body = render_template('list-mail-template.html', context)
    # print(users_groups)
    # print(response_body)
    start_response_headers = response_header_basic = {
        "status": "200 OK",
        "response_body": [
            ('Content-type', 'text/html'),
            ('Content-length', str(len(response_body))),
        ],
    }
    return response_body, start_response_headers
