from string import Template  # Create a template that has placeholder for value of x


from ...utils.session_handler import get_username_from_environ

start_response_headers: dict = {}


def groups_view(environ, **kwargs):

    # 404 if group doesnt exist
    username = get_username_from_environ(environ)
    group_name = kwargs['group_name']

    group_auth_code = "2fcfdcedfb6290fa404c8a06e366a35555f4392293c6435ff326aa06f2ebd755"

    with open('websocket_chat/clients/group_chat.html', 'r') as filereader:
        html_response = filereader.read()
    html_response = Template(html_response)
    html_response = html_response.substitute(
        {'groupname': group_name, 'username': username, "group_auth_code": group_auth_code}
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
