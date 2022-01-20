from ...utils.template_handlers import render_template

from ...utils.session_handler import get_user_from_environ
from ...orm.models import User, UserGroup, Mails
from ...orm.models import UserInbox, UserSent, User


def get_inbox(environ):

    user_id = get_user_from_environ(environ)

    Mails_table_name = Mails.objects.model_class.table_name
    User_table_name = User.objects.model_class.table_name
    Usersent_table_name = UserSent.objects.model_class.table_name
    Userinbox_table_name = UserInbox.objects.model_class.table_name

    query = f"""SELECT * FROM {Mails_table_name} Mail INNER JOIN {Userinbox_table_name} Inbox  ON (Mail.id = Inbox.mail_id)
                INNER JOIN  {Usersent_table_name} Sent ON (Inbox.mail_id = Sent.mail_id)
                INNER JOIN {User_table_name} Users ON (Users.id = Sent.user_id)
                
                WHERE Inbox.user_id = %s AND  Inbox.archived_mail = %s
                ORDER BY "created_date" DESC
            """
    parameters = [user_id, False]
    print()
    inbox = Mails.objects.raw_sql_query(query, parameters)
    print(inbox)

    return inbox
    #  {f"{Userinbox_table_name}.user_id": user_id, f"{Userinbox_table_name}.archived_mail": False},
    # print(len(inbox), type(inbox)) # 0 => <class 'list'>

    # return inbox


# actually inbox sent mails archive draft all need join btw all table
def inbox_view(environ, **kwargs):
    '''
    select is not loop, so row containing values which satisifes condition are retrieved
    rows are not multiplied here, every row with mail_id in LIST which are Archived are retrievd,
    important => data retireved never greater than data in the table
    if a user sends same mail through user, groups
    only one copy will reach here since mail id is unique which is actually good
    '''
    inbox = get_inbox(environ)
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
        <p>from:{each_mail.email}</p>
        <pre>{each_mail.body}</pre>
        {link_html_tag}
        
        <form action="/mail-user-interactions-inbox/{each_mail.mail_id}" method="post">
            <input type="submit" name="interaction" value="archive">
            <input type="submit" name="interaction" value="reply" placeholder="reply">
            <input type="submit" name="interaction" value="forward" placeholder="forward">
            <input type="submit" name="interaction" value="delete" placeholder="delete">

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
