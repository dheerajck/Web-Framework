from ...orm.models import User, Groups, UserGroup, UsersPrivateChatModel
from ...utils.session_handler import get_user_from_environ
from ...utils.template_handlers import render_template

from ...utils.session_handler import create_random_link
import psycopg2

start_response_headers: dict = {}


def get_private_chat_link(user1, user2):

    UsersPrivateChatModel_table_name = UsersPrivateChatModel.objects.model_class.table_name
    result = UsersPrivateChatModel.objects.raw_sql_query(
        f'''SELECT private_chat_link as link FROM {UsersPrivateChatModel_table_name}
            WHERE user_id_1 = {user1} AND user_id_2 = {user2} OR user_id_1 = {user2} AND user_id_2 = {user1}
            '''
    )

    # if no link, generate a link
    if result == []:
        while True:
            try:
                private_link = create_random_link()
                UsersPrivateChatModel.objects.create(
                    new_data={"user_id_1": user1, "user_id_2": user2, "private_chat_link": private_link}
                )
            except psycopg2.errors.UniqueViolation:
                pass
            else:
                private_link = private_link
                break
    else:
        private_link = result[0].link
    # print(f"private chat link of the users {user1} and {user2} is {private_link}")
    return private_link


def real_time_chat_view(environ, **kwargs):
    user_id = get_user_from_environ(environ)
    groups_object = UserGroup.objects.select({"group_id"}, {"user_id": user_id})
    groups_id = [each.group_id for each in groups_object]
    groups_id_tuple = tuple(groups_id)

    # Important if no element in group tuple, dont do orm select
    if len(groups_id_tuple) > 0:
        joined_group = Groups.objects.select({}, {"id": groups_id_tuple}, 0, 1)
    else:
        joined_group = []

    group_template = ""

    for each in joined_group:
        group_template += f"""<div>
                                <h3>{each.group_name}</h3>
                                <a href="group/{each.group_name}/"> group link</a>
                                <hr>
                            </div>
                            """
    if group_template == "":
        group_template = "No groups"

    User_table = User.objects.model_class.table_name
    query = f"SELECT * from {User_table} WHERE id != %s"
    parameter = [user_id]
    users_list = User.objects.raw_sql_query(query, parameter)

    for user in users_list:
        users_list

    users_template = ""
    # currently all users are available
    for users_in_chat in users_list:

        private_chat_link = get_private_chat_link(user_id, users_in_chat.id)
        users_template += f"""<div>
                                <h3>{users_in_chat.name} | {users_in_chat.username}</h3>
                                <a href='private-chat/{private_chat_link}/'> chat link</a>
                                <hr>
                            </div>
                            """

    # only user is the current user..
    if len(users_list) == 1:
        users_template = "No users to chat"

    context = {"groups": group_template, "users": users_template}
    html_response = render_template("real-time-chat.html", context)

    return html_response, start_response_headers
