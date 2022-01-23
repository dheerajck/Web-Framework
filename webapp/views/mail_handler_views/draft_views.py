from ...utils.template_handlers import render_template
from ...utils.session_handler import get_user_from_environ

from ...orm.models import User, Mails, UserSent, UserInbox, Groups


def get_draft_mails(environ):
    user_id = get_user_from_environ(environ)

    Groups_table_name = Groups.objects.model_class.table_name
    Userinbox_table_name = UserInbox.objects.model_class.table_name
    Mail_table_name = Mails.objects.model_class.table_name
    User_table_name = User.objects.model_class.table_name

    sent_mails = UserSent.objects.select({"mail_id"}, {"user_id": user_id, "deleted": False})
    sent_mails_mail_id = [i.mail_id for i in sent_mails]
    sent_mails_mail_tuple = tuple(sent_mails_mail_id)

    draft_mails = []
    # all join is LEFT JOIN here because there is no sure/assurance there will be data having matching colimn since this is DRAFT
    if len(sent_mails_mail_tuple) > 0:
        query = f"""SELECT Mail.id as id, Mail.created_date as created_date, Mail.title as title, Mail.body as body, Mail.attachment as attachment, Inbox.user_id as user_id, Groups.group_mail as group_mail, Users.email as user_mail
                FROM {Mail_table_name} Mail LEFT JOIN {Userinbox_table_name} Inbox ON (Mail.id = Inbox.mail_id) LEFT JOIN {Groups_table_name} Groups ON (Inbox.group_id=Groups.id) LEFT JOIN {User_table_name} Users ON (Users.id=Inbox.user_id)
                WHERE Mail.id IN %s AND Mail.draft=%s ORDER BY "created_date" DESC
                """
        parameters = [sent_mails_mail_tuple, True]
        draft_mails = Mails.objects.raw_sql_query(query, parameters)
    # print(draft_mails)
    # print(len(inbox), type(inbox)) # 0 => <class 'list'>
    return draft_mails


def get_receivers_dict(draft_mails):
    '''
    receivers_list = receivers_dict.get(each_mail.id, [])
    receivers = ", ".join(receivers_list)

    Use dict.get to get receivers list and if there is no key return an empty list []
    '''

    receivers_dict = {}
    for mail in draft_mails:

        if mail.user_mail is None:
            # if there is no user, definitely there is no group,
            # so no need to check if group_mail will have value
            continue

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

    for key in receivers_dict:
        if None in receivers_dict[key]:
            assert False, "None in receivers field, its prevented above by not adding None if user.mail is none"
    return receivers_dict


def draft_mails_view(environ, **kwargs):
    draft_mails = get_draft_mails(environ)
    # print(sent_mails)
    receivers_dict = get_receivers_dict(draft_mails)

    # print(len(draft_mails))

    # print(f"receivers dict is {receivers_dict=}")
    # print()
    # print()

    # eliminating duplicate since we got the group mail
    draft_mails = {mail.id: mail for mail in draft_mails}

    mail_div = ''

    # duplicated eliminated by making mail id a key and iterating through value to get mail object

    for each_mail in draft_mails.values():

        link_html_tag = ''
        if each_mail.attachment is not None:
            file_name = each_mail.attachment.split("__")[-1]
            file_directory = '/media/'
            file_link = f"{file_directory}{each_mail.attachment}"
            link_html_tag = f"<a download={file_name} href={file_link}>attachment link</a>"

        # generate all receivers of a sent mail

        # receivers_list = receivers_dict[each_mail.id]
        # receivers_list.remove(None)
        # if len(receivers_list) == 0:
        #     receivers = ""
        # else:
        #     receivers = ", ".join(receivers_list)

        receivers_list = receivers_dict.get(each_mail.id, [])
        receivers = ", ".join(receivers_list)

        # print("________________________")
        # print(receivers_dict)
        # print()
        # print(receivers_list, each_mail.id)
        # print("________________________")

        #  space present in comment tag after --  will make the template not render

        # <!-- add datetime sort Done -- >
        # <h3>{each_mail.id}</h3>
        mail_div += f'''
            <div>
            <!-- add datetime sort Done -->

            <h3>{each_mail.created_date}</h3>
            <h2>{each_mail.title}</h2>
            <p>To:{receivers}</p>
            <pre>{each_mail.body}</pre>
            {link_html_tag}
            <form action="/mail-user-interactions-draft/{each_mail.id}" method="post">
                <input type="submit" name="interaction" value="edit" placeholder="edit">
                <input type="submit" name="interaction" value="delete" placeholder="delete">
            </form>

            <hr>

            </div>'''

    print("s2")
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.....")

    if mail_div == "":
        mail_div = "<h1>No Draft mails</h1>"

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
