from ...utils.template_handlers import render_template

from ...utils.session_handler import get_user_from_environ
from ...orm.models import User, Mails
from ...orm.models import UserInbox, UserSent

"""
can replace using inbox view by passing one paarameter to view
which says if inbox or archive should be  shown in the display
"""


def get_archives(environ):

    user_id = get_user_from_environ(environ)

    Mails_table_name = Mails.objects.model_class.table_name
    User_table_name = User.objects.model_class.table_name
    Usersent_table_name = UserSent.objects.model_class.table_name
    Userinbox_table_name = UserInbox.objects.model_class.table_name

    query = f"""SELECT * FROM {Mails_table_name} Mail INNER JOIN {Userinbox_table_name} Inbox  ON (Mail.id = Inbox.mail_id)
                INNER JOIN  {Usersent_table_name} Sent ON (Inbox.mail_id = Sent.mail_id)
                INNER JOIN {User_table_name} Users ON (Users.id = Sent.user_id)

                WHERE Inbox.user_id = %s AND Inbox.deleted = %s AND Inbox.archived_mail = %s
                ORDER BY "created_date" DESC
            """
    parameters = [user_id, False, True]

    archives = Mails.objects.raw_sql_query(query, parameters)
    return archives


def archives_view(environ, **kwargs):

    archives = get_archives(environ)
    mail_div = ''
    for each_mail in archives:
        link_html_tag = ''

        if each_mail.attachment is not None:

            file_name = each_mail.attachment.split("__")[-1]
            file_directory = '/media/'
            file_link = f"{file_directory}{each_mail.attachment}"
            link_html_tag = f"<a download={file_name} href={file_link}>attachment link</a>"

        mail_div += f'''

        <div>

        <h3>{each_mail.created_date}</h3>
        <h2>{each_mail.title}</h2>
        <p>from:{each_mail.email}</p>
        <pre>{each_mail.body}</pre>
        {link_html_tag}

        <form action="/mail-user-interactions-archive/{each_mail.mail_id}" method="post">
            <input type="submit" name="interaction" value="unarchive">
            <button type="submit" formaction="/archives/reply/{each_mail.mail_id}/">reply</button>
            <button type="submit" formaction="/archives/forward/{each_mail.mail_id}/">forward</button>
            <input type="submit" name="interaction" value="delete" placeholder="delete">

        </form>
        <hr>
        </div>'''

    # if for loop is not executed because there are no mails in inbox of user
    if mail_div == "":
        mail_div = "<h1>No Archived mails</h1>"

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
