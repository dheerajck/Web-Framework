from ..orm.models import User, Mails, UserSent, UserInbox, UserGroup

from ..utils.datetime_module import get_current_time_tz
import uuid

# admin@admin.com
# admin_test1@admin.com

# group1@admin.com

# admin_test2@admin.com
# admin_test3@admin.com


def get_mail_data_dict(form_field_object):
    # print(form_field_object)
    # print(11, form_field_object.getvalue('attachment'))
    # print(form_field_object)
    # this should not return key error since this is name of a filed in the html form #
    #  this key will be always be present with a value or null string
    fileitem = form_field_object['attachment']
    # traversal file name
    file_name = fileitem.filename
    # form_field_storage gives all fields except files on string format, files on binary format
    # draft is false by default, "draft" is True can be add form send_draft
    mail_data = {
        'created_date': get_current_time_tz(),
        'title': form_field_object.getvalue('title'),
        'body': form_field_object.getvalue('body'),
        'attachment': fileitem.filename,
    }

    print("########################################################")
    print(mail_data)
    mail_data = {key: value for key, value in mail_data.items() if value != ''}
    print(mail_data)
    # print(22, form_field_object.getvalue('attachment'))
    if 'attachment' in mail_data:
        file_name = mail_data['attachment']
        random_string = str(uuid.uuid4())
        new_file_name = f'{random_string}__{file_name}'
        mail_data['attachment'] = new_file_name

        # saving file
        print()
        directory = 'webapp/media/'
        # file name contain extension, so no need to add it
        # saves files to media folder
        # serve this file as downloadable or viewable if browser supports
        file_path = directory + new_file_name
        with open(file_path, mode='wb') as f:
            # print(form_field_object.getvalue('attachment'))
            f.write(form_field_object.getvalue('attachment'))

    return mail_data


def send_mail(sender_id, user_list, group_list, form_field_object, draft=False):
    # delete mail if its in draft
    mail_data_dict = get_mail_data_dict(form_field_object)

    if draft is True:
        mail_data_dict["draft"] = True

    # add to mail table
    mail_id = Mails.objects.create(new_data=mail_data_dict)
    print(mail_id)
    # added mail link to UserSent Model
    UserSent.objects.create(new_data={"user_id": sender_id, "mail_id": mail_id})

    list_of_datas_user = []

    for user_id in user_list:
        list_of_datas_user.append({"user_id": user_id, "mail_id": mail_id})

    if len(list_of_datas_user) != 0:
        """
        add users who received the mail
        """
        UserInbox.objects.bulk_insert(list_of_datas_user)

    memebers_list_from_all_groups = []
    # implemented to return empty list if field in A, if A is empty container
    if len(group_list) > 0:
        memebers_list_from_all_groups = UserGroup.objects.select(
            {"user_id", "group_id"},
            {"group_id": group_list},
            0,  # only one element in filter filed so AND or OR gives will both will have no effect here
            1,
        )

    list_of_datas_user_with_group_id = []
    for users in memebers_list_from_all_groups:
        list_of_datas_user_with_group_id.append(
            {"user_id": users.user_id, "group_id": users.group_id, "mail_id": mail_id}
        )

    if len(list_of_datas_user_with_group_id) != 0:
        """
        add users who received the mail
        """
        UserInbox.objects.bulk_insert(list_of_datas_user_with_group_id)

    # multiple insert orm create

    # multiple insert user foreign key

    # multiple insert group foreign key


def send_draft(sender_id, user_list, group_list, form_field_object):
    draft_data_dict = get_mail_data_dict(form_field_object)
    send_mail(sender_id, user_list, group_list, form_field_object, draft=True)
