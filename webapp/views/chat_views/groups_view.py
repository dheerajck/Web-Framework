from string import Template  # Create a template that has placeholder for value of x


from ...utils.session_handler import get_username_from_environ

start_response_headers: dict = {}


def groups_view(environ, **kwargs):

    username = get_username_from_environ(environ)
    group_name = kwargs['group_name']
    with open('websocket_chat/index.html', 'r') as filereader:
        html_response = filereader.read()
    html_response = Template(html_response)
    html_response = html_response.substitute({'groupname': group_name, 'username': username})
    return html_response, start_response_headers


if __name__ == "__main__":
    # dont user render template,
    from string import Template  # Create a template that has placeholder for value of x

    t = Template('x is $groupname')
    print(t.substitute({'groupname': 1, 'username': 2}))
    x is 1
