from ...utils.template_handlers import render_template

from ...utils.session_handler import get_user_from_environ
from ...orm.models import User, UserGroup
from ...orm.models import Drafts, DraftReceivers


def view_draft_mails(environ, **kwargs):

    receivers_list = []
    user_id = get_user_from_environ(environ)
    users_groups = UserGroup.objects.select({"group_id"}, {'user_id': user_id})
    print(users_groups)
    users_groups_id = [user.group_id for user in users_groups]

    users_groups_id = tuple(users_groups_id)
    print(user_id, users_groups_id)
    print("^^^^^^^^^^^^^^^^^^^^^^^^")

    print("DRAFT USER")
    print("user id", user_id)
    # 1 => OR 1 => IN
    draft_mails_id_objects = DraftReceivers.objects.select(
        {"draft_id"},
        {"receiver_user": user_id, "receiver_group": users_groups_id},
        1,  # 1 => OR
        1,  # 1 => field IN tuples , 0 => field=value
    )
    draft_mails_id_list = [mail_object.mail_id for mail_object in draft_mails_id_objects]
    print(draft_mails_id_list, "FOUND")

    draft_mails_id_tuple = tuple(draft_mails_id_list)

    filter_condition = {"id": draft_mails_id_tuple}
    print(draft_mails_id_list, "FOUND")
    if len(draft_mails_id_tuple) == 0:
        print("no draft")
        filter_condition = {}

    draft_mail_objects = Drafts.objects.select(
        {},
        filter_condition,
        0,  # 0 => AND
        1,  # 1 => field IN tuples , 0 => field=value
        ("created_date",),  # order by created_date descending order
    )
    print(draft_mail_objects)

    mail_div = ''
    for each_draft_mail in draft_mail_objects:

        link_html_tag = ''
        if each_draft_mail.attachment is not None:
            file_name = each_draft_mail.attachment.split("__")[-1]
            file_directory = '/media/'
            file_link = f"{file_directory}{each_draft_mail.attachment}"
            link_html_tag = f"<a download={file_name} href={file_link}>attachment link</a>"

        #  space present in comment tag after --  will make the template not render
        # <!-- add datetime sort Done -- >
        mail_div += f'''
        
        <div>
         <!-- add datetime sort Done -->
      
        
        <h3>{each_draft_mail.created_date}</h3>
        <h2>{each_draft_mail.title}</h2>
        <p>from:{User.objects.select_one(["email"], {"id":each_draft_mail.sender})}</p>
        <pre>{each_draft_mail.body}</pre>
        {link_html_tag}
        <form action="inbox-actions/" method="post">
            <input type="button" name="interaction" value="edit-mail" placeholder="edit-mail">
        </form>
        <hr>
        </div>'''

    # if for loop is not executed because there are no mails in draftbox of user
    if mail_div == "":
        mail_div = "<h1>No mails in Draft</h1>"
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
