from ..orm.models import User


def authentication_user(username, password):

    # print("Created a Userobject and inserted")
    UserObject = User.objects.select({'id'}, {'username': username, 'password': password})
    # both username an password fields are required so doing assert not None here
    assert None not in (username, password)

    # print(username, password)
    # print("HI this is test", UserObject)

    # fetchmany is used in orm so [] is returned is user details doesnt match
    # fetchone will return None if there are no match
    if UserObject == []:
        return False

    return UserObject[0].id
