from ...utils.template_handlers import render_template
from ...utils.session_handler import get_user_from_environ

from ...orm.models import User, Groups
from ...orm.models import Drafts, DraftReceivers


def draft_mails_view(environ, **kwargs):
    user_id = get_user_from_environ(environ)
    sent_drafts = Drafts.objects.select(
        {},
        {"sender": user_id},
        0,
        0,
        ("created_date",),
    )
    print(sent_drafts)
    print("[[[[[[[")

    mail_div = ''
    print("s1")
    for each_mail in sent_drafts:

        link_html_tag = ''
        if each_mail.attachment is not None:
            file_name = each_mail.attachment.split("__")[-1]
            file_directory = '/media/'
            file_link = f"{file_directory}{each_mail.attachment}"
            link_html_tag = f"<a download={file_name} href={file_link}>attachment link</a>"

        # generate all receivers of a draft
        receivers_list = []
        mail_id = each_mail.id
        receivers_objects = DraftReceivers.objects.select(['receiver_user', 'receiver_group'], {"draft_id": mail_id})
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
                receivers_list.append(Groups.objects.select_one(['group_mail'], {"id": receiver.receiver_group}))
            else:
                receivers_list.append(User.objects.select_one(['email'], {"id": receiver.receiver_user}))

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
        {link_html_tag}
        <form action="inbox-actions/" method="post">
            <input type="button" name="interaction" value="reply" placeholder="reply">
            <input type="button" name="interaction" value="delete" placeholder="delete">
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
