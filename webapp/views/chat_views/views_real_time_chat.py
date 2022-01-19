from ...orm.models import User, Groups, UserGroup
from ...utils.session_handler import get_user_from_environ
from ...utils.template_handlers import render_template

start_response_headers: dict = {}


def real_time_chat_view(environ, **kwargs):
    user_id = get_user_from_environ(environ)
    print(user_id)
    groups_object = UserGroup.objects.select({"group_id"}, {"user_id": user_id})
    print(groups_object)
    groups_id = [each.group_id for each in groups_object]
    groups_id_tuple = tuple(groups_id)

    # Important if no element in group tuple, dont do orm  elect
    if len(groups_id_tuple) > 0:
        joined_group = Groups.objects.select({}, {"id": groups_id_tuple}, 0, 1)
    else:
        joined_group = []

    group_template = ""
    for each in joined_group:
        group_template += f"""<div>
                                <h2>{each.group_name}</h2>
                                <a href="group/{each.group_name}"> group link</a>
                                <hr>
                            </div>
                            """
    if group_template == "":
        group_template = "No groups"

    context = {"groups": group_template}
    html_response = render_template("real-time-chat.html", context)

    return html_response, start_response_headers
