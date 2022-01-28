from ...utils.session_handler import get_user_from_environ

from ...orm.models import User, Mails
from ...orm.models import UserInbox, UserSent

from webapp.api.views1 import api_view_405, success_api_response


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
    print()
    archives = Mails.objects.raw_sql_query(query, parameters)
    # print(archives)

    return archives


def archives_api_view(environ, **kwargs):

    if environ['REQUEST_METHOD'].upper() != 'GET':
        kwargs = {"allowed": ("GET",)}
        return api_view_405(environ, **kwargs)

    archives = get_archives(environ)

    result_list = []
    for each_mail in archives:
        # print(each_mail)

        link_html_tag = False

        if each_mail.attachment is not None:

            file_name = each_mail.attachment.split("__")[-1]
            file_directory = '/media/'
            file_link = f"{file_directory}{each_mail.attachment}"
            print(file_link, "xas")
            # link_html_tag = f"<a href={file_link}>attachment link</a>"
            link_html_tag = f"{file_link}"

        dictionary_of_mail_object = {
            "mail_id": each_mail.mail_id,
            "Created_date": each_mail.created_date.isoformat(),
            "Title": each_mail.title,
            "From": each_mail.email,
            "Body": each_mail.body,
        }

        if link_html_tag:
            dictionary_of_mail_object["attachment_link"] = link_html_tag

        result_list += [dictionary_of_mail_object]

    if result_list == []:
        result_list = "No mail in archive"
    return success_api_response(result_list)
