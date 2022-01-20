from ...utils.template_handlers import render_template
from ...utils.session_handler import get_user_from_environ

from ...orm.models import User, Mails, UserSent, UserInbox, Groups


def get_send_mails(environ):
    user_id = get_user_from_environ(environ)

    Groups_table_name = Groups.objects.model_class.table_name
    Userinbox_table_name = UserInbox.objects.model_class.table_name
    Mail_table_name = Mails.objects.model_class.table_name
    User_table_name = User.objects.model_class.table_name

    sent_mails = UserSent.objects.select({"mail_id"}, {"user_id": user_id, "deleted": False})
    sent_mails_mail_id = [i.mail_id for i in sent_mails]
    sent_mails_mail_tuple = tuple(sent_mails_mail_id)

    sent_mails = []
    if len(sent_mails_mail_tuple) > 0:
        query = f"""SELECT Mail.id as id, Mail.created_date as created_date, Mail.title as title, Mail.body as body, Mail.attachment as attachment, Inbox.user_id as user_id, Groups.group_mail as group_mail, Users.email as user_mail
                FROM {Mail_table_name} Mail INNER JOIN {Userinbox_table_name} Inbox ON (Mail.id = Inbox.mail_id) LEFT JOIN {Groups_table_name} Groups ON (Inbox.group_id=Groups.id) 
                INNER JOIN {User_table_name} Users ON (Users.id=Inbox.user_id)
                
                WHERE Mail.id IN %s AND Mail.draft=%s ORDER BY "created_date" DESC
                """
        parameters = [sent_mails_mail_tuple, False]
        sent_mails = Mails.objects.raw_sql_query(query, parameters)
    print(sent_mails)
    return sent_mails
    # print(len(inbox), type(inbox)) # 0 => <class 'list'>


def sent_mail_view(environ, **kwargs):

    sent_mails = get_send_mails(environ)
    # print(sent_mails)
    receivers_dict = {}

    print('strtasdsa')
    print(len(sent_mails))

    for mail in sent_mails:

        if mail.id in receivers_dict:
            value = receivers_dict[mail.id]

            if mail.group_mail is not None:
                value.add(mail.group_mail)
            else:
                value.add(mail.user_mail)
            receivers_dict[mail.id] = value

        else:
            if mail.group_mail is not None:
                receivers_dict[mail.id] = {mail.group_mail}
            else:
                receivers_dict[mail.id] = {mail.user_mail}

    print(f"receivers dict is {receivers_dict=}")
    print()
    print()

    # eliminating duplicate since we got the group mail
    sent_mails = {mail.id: mail for mail in sent_mails}

    mail_div = ''
    print(f"{sent_mails=}\nlength {len(sent_mails)}")
    print()
    print()
    # duplicated eliminated by making mail id a key and iterating through value to get mail object

    # for a, each_mail in sent_mails.items():
    for each_mail in sent_mails.values():
        # print(f"{a=} {receivers_dict[a]=}") helped to debug similar name confusing error mail.id and each_mail.id
        link_html_tag = ''
        if each_mail.attachment is not None:
            file_name = each_mail.attachment.split("__")[-1]
            file_directory = '/media/'
            file_link = f"{file_directory}{each_mail.attachment}"
            link_html_tag = f"<a download={file_name} href={file_link}>attachment link</a>"

        # generate all receivers of a sent mail
        receivers_list = ", ".join(receivers_dict[each_mail.id])
        print("________________________")
        print(receivers_dict)
        print()
        print(receivers_list, mail.id)
        print("________________________")

        #  space present in comment tag after --  will make the template not render

        # <!-- add datetime sort Done -- >
        #    <h3>{each_mail.id}</h3>
        mail_div += f'''
            <div>
            <!-- add datetime sort Done -->
        
        
            
            <h3>{each_mail.created_date}</h3>
            <h2>{each_mail.title}</h2>
            <p>To:{receivers_list}</p>
            <pre>{each_mail.body}</pre>
            {link_html_tag}
            <form action="/mail-user-interactions-sent/{each_mail.id}" method="post">
                <input type="submit" name="interaction" value="delete" placeholder="delete">
            </form>
            <hr>
            </div>'''
    print("s2")
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.....")

    if mail_div == "":
        mail_div = "<h1>No Sent mails</h1>"

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


if __name__ == "__main__":
    pass
    # this wasnt working because of user id
    # inbox = Mails.objects.model_independent_select_join(
    # {},
    # {f"{Usersent_table_name}.user_id": user_id, f"{Mail_table_name}.draft": False},
    # 0,  # 0 => AND
    # 1,  # 1 => field IN tuples , 0 => field=value
    # ("created_date",),  # order by created_date descending order
    # join_model=[
    #     (Groups_table_name, "id", "group_id"),
    #     (Userinbox_table_name, "X", "user_id"),
    #     (Mail_table_name, "user_id", "id"),
    #     (Usersent_table_name, "id", "user_id"),
    #     (User_table_name, "user_id", "id"),
    # ],
