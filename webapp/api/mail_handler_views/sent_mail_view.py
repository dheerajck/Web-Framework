from ...utils.session_handler import get_user_from_environ

from ...orm.models import User, Mails, UserSent, UserInbox, Groups

from webapp.api.views1 import api_view_405

import json

def success_api_response(message):
    status = "200 OK"
    response_headers = [
        ('Content-type', 'application/json'),
    ]

    response_body = {'message': message, 'status': status}
    response_body = json.dumps(response_body, indent=4)
    

    response_headers.append(('Content-length', str(len(response_body))))
    start_response_headers: dict = {'status': status, 'response_headers': response_headers}
    return response_body, start_response_headers


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


def sent_mail_api_view(environ, **kwargs):
    
    if environ['REQUEST_METHOD'].upper() != 'GET':
        kwargs = {"allowed": ("GET",)}
        return api_view_405(environ, **kwargs)



    sent_mails = get_send_mails(environ)
    # print(sent_mails)
    receivers_dict = {}

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


    # eliminating duplicate since we got the group mail
    sent_mails = {mail.id: mail for mail in sent_mails}

    result_list = []


    for each_mail in sent_mails.values():
        # print(f"{a=} {receivers_dict[a]=}") helped to debug similar name confusing error mail.id and each_mail.id
        link_html_tag = False
        if each_mail.attachment is not None:
            file_name = each_mail.attachment.split("__")[-1]
            file_directory = '/media/'
            file_link = f"{file_directory}{each_mail.attachment}"
            link_html_tag = f"{file_link}"
         
         
        receivers_string = ", ".join(receivers_dict[each_mail.id])
         
        dictionary_of_mail_object = {
            "mail_id": each_mail.id,
            "Created_date": each_mail.created_date.isoformat(),
            "Title": each_mail.title,
            "Receivers_list": receivers_string,
            "Body": each_mail.body,
        }   


        if link_html_tag:
            dictionary_of_mail_object["attachment_link"] = link_html_tag

        result_list += [dictionary_of_mail_object]
        

    # if result_list == []: result_list = ["No sent mails"]
    if result_list == []: result_list = "No sent mails"

    return success_api_response(result_list)


