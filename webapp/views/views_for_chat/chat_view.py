from string import Template  # Create a template that has placeholder for value of x


from ...utils.session_handler import get_user_details_from_environ
from ...utils.session_handler import get_user_details_from_id
from ...orm.models import UsersPrivateChatModel

start_response_headers: dict = {}


def chat_view(environ, **kwargs):

    # 404 if group doesnt exist
    # username = get_username_from_environ(environ)
    user_details = get_user_details_from_environ(environ, ["id", "username"])
    user_id, username = user_details

    chat_link = kwargs['chat_link']
    # input(f'{chat_link}')

    # select_one retuns a list containing fields in select,
    # select_one returns a list of objects as results

    users_in_the_chat = UsersPrivateChatModel.objects.select_one(
        ["user_id_1", "user_id_2"], {"private_chat_link": chat_link}
    )

    if users_in_the_chat:
        # private chat
        user_1, user_2 = users_in_the_chat
        other_user = {user_1, user_2} - {user_id}
        other_user_id = other_user.pop()
        other_user_details = get_user_details_from_id(user_id=other_user_id, field=["username", "name"])

        chat_name = f"Chatting with {other_user_details[1]}"

    else:
        # group chat
        chat_name = f"Group chat => {chat_link}"
    # <h2>Group chat => $chat_name</h2>
    # _______________________________________________________________________________________

    chat_auth_code = "2fcfdcedfb6290fa404c8a06e366a35555f4392293c6435ff326aa06f2ebd755"

    with open('websocket_chat/clients/group_chat.html', 'r') as filereader:
        html_response = filereader.read()

    html_response = Template(html_response)

    html_response = html_response.substitute(
        {
            'chat_link': chat_link,
            'chat_name': chat_name,
            'username': username,
            "chat_auth_code": chat_auth_code,
        }
    )
    return html_response, start_response_headers


if __name__ == "__main__":
    print("testing_template_main_function")
    # dont user render template,
    # javascript contains {} which will result in issues with format and fstring,
    # so another formating is used here

    """from string import Template  # Create a template that has placeholder for value of x

    t = Template('x is $groupname')
    print(t.substitute({'groupname': 1, 'username': 2}))
    x is 1
    """
