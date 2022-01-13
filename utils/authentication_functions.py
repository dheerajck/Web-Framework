# from ..orm.models import User


def authentication_user(username, password):
    UserObject = User.objects.select({'id'}, {'username': username, 'password': password})

    # fetchmany is used in orm so [] is returned is user details doesnt match
    # fetchone will return None if there are no match
    if UserObject == []:
        return False

    return UserObject[0].id
