from ..utils.template_handlers import render_template

from ..utils.post_form_handler import cgiFieldStorageToDict
from ..utils.post_form_handler import form_with_file_parsing

from ..utils.datetime_module import get_current_time_tz


from ..utils.session_handler import get_user_from_environ

# from webapp.utils.post_form_handler import cgiFieldStorageToDict


from ..utils.redirect_functions import redirect_to_dashboard_module

start_response_headers: dict = {}

from ..orm.models import User, Groups, UserGroup


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


from ..utils.mail_utilites import send_mail, send_draft


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


# assert 0, 'Created views to display sent mails, archived mails, drafts.'


def view_sent_mails(environ, **kwargs):
    user_id = get_user_from_environ(environ)
    sent_mails = Mails.objects.select({}, {"sender": user_id})
    print(sent_mails)
    print("[[[[[[[")

    mail_div = ''
    print("s1")
    for each_mail in sent_mails:

        receivers_list = []
        mail_id = each_mail.id
        receivers_objects = MailReceivers.objects.select(['receiver_user', 'receiver_group'], {"mail_id": mail_id})
        print(receivers_objects)
        #  space present in comment tag after --  will make the template not render
        for receiver in receivers_objects:
            print(type(receiver.receiver_user))
            print("hi")
            receiver_user = receiver.receiver_user
            print(receiver_user)
            if receiver_user is None:
                # then definitely there will be a group
                # one constraint should have value
                receivers_list.append(Groups.objects.select_one(['group_mail'], {"id": receiver.receiver_group})[0])
            else:
                receivers_list.append(User.objects.select_one(['email'], {"id": receiver.receiver_user})[0])

        print(receivers_list)
        receivers_list = ", ".join(receivers_list)
        print("yessssssssssssssssssssss")

        # <!-- add datetime sort Done -- >
        mail_div += f'''
        
        <div>
         <!-- add datetime sort Done -->
      
        
        <h3>{each_mail.created_date}</h3>
        <h2>{each_mail.title}</h2>
        <p>To:{receivers_list}</p>
        <pre>{each_mail.body}</pre>
        <a href="">attachement link</a>
        <form action="inbox-actions/" method="post">
            <input type="button" name="interaction" value="reply" placeholder="reply">
            <input type="button" name="interaction" value="delete" placeholder="delete">
        </form>
        <hr>
        </div>'''
    print("s2")
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.....")

    from ..utils.template_handlers import render_template

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


def view_draft(environ, **kwargs):
    pass


from ..orm.models import Mails, MailReceivers


def view_inbox(environ, **kwargs):

    receivers_list = []
    user_id = get_user_from_environ(environ)
    users_groups = UserGroup.objects.select({"group_id"}, {'user_id': user_id})
    print(users_groups)
    users_groups_id = [user.group_id for user in users_groups]

    users_groups_id = tuple(users_groups_id)
    print(users_groups)

    print("INBOX USER")
    print("user id", user_id)
    # 1 => OR 1 => IN
    mails_id_objects = MailReceivers.objects.select(
        {"mail_id"},
        {"receiver_user": user_id, "receiver_group": users_groups_id},
        1,  # 1 => OR
        1,  # 1 => field IN tuples , 0 => field=value
    )
    mails_id_list = [mail_object.mail_id for mail_object in mails_id_objects]
    print(mails_id_list, "FOUND")

    mails_id_tuple = tuple(mails_id_list)
    inbox = Mails.objects.select(
        {},
        {"id": mails_id_tuple, "archives": False},
        0,  # 0 => OR
        1,  # 1 => field IN tuples , 0 => field=value
        ("created_date",),
    )
    print(inbox)

    mail_div = ''
    for each_mail in inbox:
        #  space present in comment tag after --  will make the template not render
        # <!-- add datetime sort Done -- >
        mail_div += f'''
        
        <div>
         <!-- add datetime sort Done -->
      
        
        <h3>{each_mail.created_date}</h3>
        <h2>{each_mail.title}</h2>
        <p>from:{User.objects.select_one(["email"], {"id":each_mail.sender})[0]}</p>
        <pre>{each_mail.body}</pre>
        <a href="">attachement link</a>
        <form action="inbox-actions/" method="post">
            <input type="button" name="interaction" value="archive" placeholder="archive">
            <input type="button" name="interaction" value="reply" placeholder="reply">
            <input type="button" name="interaction" value="delete" placeholder="delete">
        </form>
        <hr>
        </div>'''

    from ..utils.template_handlers import render_template

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


def view_archived_mails(environ, **kwargs):
    pass
