from .orm_manager import BaseModel, BaseManager
import psycopg2


class User(BaseModel):
    manager_class = BaseManager
    table_name = "app_users"


class Mails(BaseModel):
    manager_class = BaseManager
    table_name = "mails"


class Groups(BaseModel):
    manager_class = BaseManager
    table_name = "groups"


class UserGroup(BaseModel):
    manager_class = BaseManager
    table_name = "user_group"


class UserSent(BaseModel):
    manager_class = BaseManager
    table_name = "user_sent"


class UserInbox(BaseModel):
    manager_class = BaseManager
    table_name = "user_inbox"


class Session(BaseModel):
    manager_class = BaseManager
    table_name = "session"


if __name__ == "__main__":
    try:
        User.objects.create(
            new_data={'name': 'admin', 'username': 'username_admin', 'email': 'admin@admin.admin', 'password': 'admin'}
        )

    except psycopg2.errors.UniqueViolation:
        print("what check")

    try:
        Groups.objects.create(new_data={'group_mail': 'group@group.mail'})
    except psycopg2.errors.UniqueViolation:
        print("what duplicate is not allowed using unique constraint")
    # Groups.objects.update(new_data={'group_mail': "A"}, conditions_dict={'id': 1})
    # a = Groups.objects.select({}, {'id': 1})
    # print(a)
    # Groups.objects.create(new_data={'group_mail': "1"})
    # a = Groups.objects.select({}, {'id': 2})

    # print(1)
    # print(a)
    # print(vars(a[0]))

    # a = Groups.objects.select({}, {'id': 2})

    # print(1)
    # print(a)
    # print("_________________________________________________________-----")
    # print('first printing')
    # print(a[0].group_mail)
    # print(a)
    # print("_________________________________________________________-----")
    # print(vars(a[0]))

    # Groups.objects.update(new_data={'group_mail': "a1"})

    # a = Groups.objects.select({}, {})

    # print("_________________________________________________________-----")
    # print(a[0].group_mail)
    # print(a)
    # print("_________________________________________________________-----")
    # print(vars(a[0]))
