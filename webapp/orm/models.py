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


class UsersPrivateChatModel(BaseModel):
    manager_class = BaseManager
    table_name = "users_private_chat"


class SessionDb(BaseModel):
    manager_class = BaseManager
    table_name = "session_db_table"


if __name__ == "__main__":
    try:
        User.objects.create(
            new_data={'name': 'admin', 'username': 'username_admin', 'email': 'admin@admin.admin', 'password': 'admin'}
        )

    except psycopg2.errors.UniqueViolation:
        print("data with same field value on unique field exist in db")

    try:
        Groups.objects.create(new_data={'group_mail': 'group@group.mail'})
    except psycopg2.errors.UniqueViolation:
        print("data with same field value on unique field exist in db")
