from ..orm.models import User, Mails, Drafts, MailReceivers, DraftReceivers

from ..utils.datetime_module import get_current_time_tz
import uuid

# admin@admin.com
# admin_test1@admin.com

# group1@admin.com

# admin_test2@admin.com
# admin_test3@admin.com


def get_mail_data_dict(sender_id, form_field_object):
    # print(form_field_object)
    # print(11, form_field_object.getvalue('attachment'))
    # print(form_field_object)
    # this should not return key error since this is name of a filed in the html form #
    #  this key will be always be present with a value or null string
    fileitem = form_field_object['attachment']
    # traversal file name
    file_name = fileitem.filename
    # form_field_storage gives all fields except files on string format, files on binary format
    mail_data = {
        'created_date': get_current_time_tz(),
        'sender': sender_id,
        'title': form_field_object.getvalue('title'),
        'body': form_field_object.getvalue('body'),
        # archives: 1,
        'attachment': fileitem.filename,
    }

    mail_data = {key: value for key, value in mail_data.items() if value != ''}
    # print(22, form_field_object.getvalue('attachment'))
    if 'attachment' in mail_data:
        file_name = mail_data['attachment']
        random_string = str(uuid.uuid4())
        new_file_name = f'{random_string}__{file_name}'
        mail_data['attachment'] = new_file_name

        # saving file
        print()
        directory = 'webapp/media/'
        file_path = directory + new_file_name
        with open(file_path, mode='wb') as f:
            # print(form_field_object.getvalue('attachment'))
            f.write(form_field_object.getvalue('attachment'))

    return mail_data


def add_receiver_to_table():
    pass


def send_mail(sender_id, user_list, group_list, form_field_object):
    # delete mail if its in draft
    mail_data_dict = get_mail_data_dict(sender_id, form_field_object)

    # add to mail table
    mail_id = Mails.objects.create(new_data=mail_data_dict)
    print(mail_id)

    list_of_datas_user = []

    for user_id in user_list:
        list_of_datas_user.append({"mail_id": mail_id, "receiver_user": user_id})

    if len(list_of_datas_user) != 0:
        """
        add users who received the mail
        """
        MailReceivers.objects.bulk_insert(list_of_datas_user)

    list_of_datas_group = []
    for group_id in group_list:
        list_of_datas_group.append({"mail_id": mail_id, "receiver_group": group_id})

    if len(list_of_datas_group) != 0:
        """
        add groups who received the mail
        """
        MailReceivers.objects.bulk_insert(list_of_datas_group)

    # multiple insert orm create

    # multiple insert user foreign key

    # multiple insert group foreign key


def send_draft(sender_id, user_list, group_list, form_field_object):
    # delete mail if its in draft
    draft_data_dict = get_mail_data_dict(sender_id, form_field_object)
    print(draft_data_dict)
    print("Check 1")
    # add to draft table
    draft_id = Drafts.objects.create(new_data=draft_data_dict)
    print("draft test1", draft_id)

    list_of_datas_user = []

    for user_id in user_list:
        list_of_datas_user.append({"draft_id": draft_id, "receiver_user": user_id})
    print("yes")
    print(list_of_datas_user)

    if len(list_of_datas_user) != 0:
        DraftReceivers.objects.bulk_insert(list_of_datas_user)

    list_of_datas_group = []
    for group_id in group_list:
        list_of_datas_group.append({"draft_id": draft_id, "receiver_group": group_id})

    if len(list_of_datas_group) != 0:
        DraftReceivers.objects.bulk_insert(list_of_datas_group)
